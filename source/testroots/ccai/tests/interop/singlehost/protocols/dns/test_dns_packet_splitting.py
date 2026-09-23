
import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from ccai.interop.protocols.dns.dnsrecord import DnsRecord
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass, DnsQr, DnsOpCode, DnsRespCode
from ccai.interop.protocols.dns.dnsflags import DnsFlags
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsaddress import DnsAddress

class _BigRecord(DnsRecord):
    """Record that writes a large payload."""
    def __init__(self, name: str, size: int, char: bytes) -> None:
        super().__init__(name, DnsRecordType.NULL, DnsRecordClass.IN, ttl=10)
        self._size = size
        self._char = char
        # Pre-generate content to ensure writing is fast and consistent
        self._content = char * size

    def write(self, out: DnsOutboundMessage) -> None:
        out.write(self._content)
        return

def test_packet_splitting_correctly_preserves_records() -> None:
    """
    Test that when records are split across packets, none are lost or duplicated.
    """
    # Setup
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # 800 bytes - fits in P1 (MAX_MSG_TYPICAL=1460, header=12, leaves ~1448)
    rec_a = _BigRecord("rec_a.local.", 800, b'A')
    
    # 800 bytes - fails P1 (800+800 > 1460), fits P2
    rec_b = _BigRecord("rec_b.local.", 800, b'B')
    
    # 100 bytes - fits P2 (after rec_b)
    rec_c = _BigRecord("rec_c.local.", 100, b'C')
    
    msg.add_answer(rec_a)
    msg.add_answer(rec_b)
    msg.add_answer(rec_c)
    
    # Execute
    packets = msg.packets()
    
    # Verify
    testbase.assert_equal(len(packets), 2)
    
    # We can inspect the raw bytes of the packets to verify content validity
    p1 = packets[0]
    p2 = packets[1]
    
    # Verify P1 contains A
    testbase.assert_equal(b'A'*800 in p1, True)
    testbase.assert_equal(b'B'*800 in p1, False)
    testbase.assert_equal(b'C'*100 in p1, False)
    
    # Verify P2 contains B and C
    testbase.assert_equal(b'A'*800 in p2, False)
    testbase.assert_equal(b'B'*800 in p2, True)
    testbase.assert_equal(b'C'*100 in p2, True)
    return

def test_packet_splitting_single_oversized_record() -> None:
    """
    Test that a single record larger than typical size is allowed in a packet if it's the only one (or first one).
    Dimensions: MAX_MSG_TYPICAL=1460, MAX_MSG_ABSOLUTE=8966.
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # 2000 bytes - larger than typical but smaller than absolute
    rec_huge = _BigRecord("huge.local.", 2000, b'H')
    
    msg.add_answer(rec_huge)
    packets = msg.packets()
    
    testbase.assert_equal(len(packets), 1)
    testbase.assert_equal(b'H'*2000 in packets[0], True)
    return

def test_packet_splitting_mixed_types() -> None:
    """
    Test correct splitting with answers and authorities.
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # Answer: 800 bytes
    rec_ans = _BigRecord("ans.local.", 800, b'A')
    
    # Authority: 800 bytes (Should force new packet if added after answer)
    rec_auth = _BigRecord("auth.local.", 800, b'U')
    
    msg.add_answer(rec_ans)
    msg.add_authoritative_answer(rec_auth)
    
    packets = msg.packets()
    
    testbase.assert_equal(len(packets), 2)
    testbase.assert_equal(b'A'*800 in packets[0], True)
    testbase.assert_equal(b'U'*800 in packets[1], True)
    testbase.assert_equal(b'U'*800 in packets[1], True)
    return

def test_packet_splitting_reverts_compression_state() -> None:
    """
    Test that when a record is rejected/split from a packet, any compression state (names) 
    added by that record are also rolled back.
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # 1. Add a small answer to start the packet.
    rec_start = _BigRecord("start.local.", 10, b'S')
    msg.add_answer(rec_start)
    
    # 2. Add a HUGE answer that introduces a new name "unique-buggy-name.local."
    # This must fit in MAX_MSG_ABSOLUTE but FAIL MAX_MSG_TYPICAL limit when added to P1.
    # It will trigger a rollback.
    rec_huge = _BigRecord("unique-buggy-name.local.", 1500, b'H')
    msg.add_answer(rec_huge)
    
    # 3. Add another small record that uses the SAME name "unique-buggy-name.local."
    # If rollback failed, this record will use a compression pointer to the 
    # removed 'rec_huge' name offset, which is invalid in the resulting packet.
    # If rollback worked, this will be written as a full name (or new compression entry).
    # IMPORTANT: This must be an AUTHORITY record so it is attempted in the SAME packet (P1)
    # after the answer loop breaks due to the huge record.
    rec_check = _BigRecord("unique-buggy-name.local.", 10, b'C')
    msg.add_authoritative_answer(rec_check)
    
    packets = msg.packets()
    
    # Verify we have split packets
    testbase.assert_equal(len(packets), 2)
    
    # Verify P1 is valid by parsing it
    p1 = packets[0]
    
    try:
        parsed = DnsInboundMessage(p1)
        # Verify success. 
        # Note: DnsInboundMessage skips NULL records, so parsed.answers will be empty.
        # But successful parsing means the name compression pointers were valid.
        testbase.assert_equal(parsed.valid, True)
    except Exception as e:
        # Use a known assertion or raise
        print(f"Packet 1 parsing failed: {e}")
        # Re-raise to fail the test properly with stack trace
        raise e
        
    return

def test_packet_splitting_large_authority_record() -> None:
    """
    Test that a single large Authority record is allowed (via allow_long logic).
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # Large record (> 1460)
    rec_huge = _BigRecord("huge-auth.local.", 2000, b'H')
    msg.add_authoritative_answer(rec_huge)
    
    packets = msg.packets()
    
    testbase.assert_equal(len(packets), 1)
    testbase.assert_equal(b'H'*2000 in packets[0], True)
    return

def test_packet_splitting_large_additional_record() -> None:
    """
    Test that a single large Additional record is allowed (via allow_long logic).
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # Large record (> 1460)
    rec_huge = _BigRecord("huge-add.local.", 2000, b'A')
    msg.add_additional_answer(rec_huge)
    
    packets = msg.packets()
    
    testbase.assert_equal(len(packets), 1)
    testbase.assert_equal(b'A'*2000 in packets[0], True)
    return

def test_packet_splitting_does_not_duplicate_questions() -> None:
    """
    Test that questions are not duplicated in subsequent packets.
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # Add a question
    q = DnsQuestion("test.local.", DnsRecordType.A, DnsRecordClass.IN)
    msg.add_question(q)

    # Add enough answers to force a split
    rec_a = _BigRecord("rec_a.local.", 800, b'A')
    rec_b = _BigRecord("rec_b.local.", 800, b'B')
    
    msg.add_answer(rec_a)
    msg.add_answer(rec_b)
    
    packets = msg.packets()
    
    testbase.assert_equal(len(packets), 2)
    
    # Packet 1 should have QDCOUNT=1
    p1 = packets[0]
    p1_qdcount = int.from_bytes(p1[4:6], byteorder='big')
    testbase.assert_equal(p1_qdcount, 1)
    
    # Packet 2 should have QDCOUNT=0
    p2 = packets[1]
    p2_qdcount = int.from_bytes(p2[4:6], byteorder='big')
    testbase.assert_equal(p2_qdcount, 0)
    return

def test_parsing_split_sections() -> None:
    """
    Test that DnsInboundMessage correctly parses records into their respective sections
    (Answers, Authorities, Additionals) instead of flattening them.
    """
    flags = DnsFlags(qr=DnsQr.Response, opcode=DnsOpCode.Query, aa=True, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # 1. Answer
    rec_ans = DnsAddress("ans.local.", DnsRecordType.A, DnsRecordClass.IN, 100, b"\x01\x02\x03\x04")
    msg.add_answer(rec_ans)
    
    # 2. Authority
    rec_auth = DnsAddress("auth.local.", DnsRecordType.A, DnsRecordClass.IN, 100, b"\x05\x06\x07\x08")
    msg.add_authoritative_answer(rec_auth)
    
    # 3. Additional
    rec_add = DnsAddress("add.local.", DnsRecordType.A, DnsRecordClass.IN, 100, b"\x09\x10\x11\x12")
    msg.add_additional_answer(rec_add)
    
    packets = msg.packets()
    testbase.assert_equal(len(packets), 1)
    
    # Parse back
    in_msg = DnsInboundMessage(packets[0])
    
    # Verify counts
    testbase.assert_equal(len(in_msg.answers), 1)
    testbase.assert_equal(len(in_msg.authorities), 1)
    testbase.assert_equal(len(in_msg.additionals), 1)
    
    # Verify content
    testbase.assert_equal(in_msg.answers[0].name, "ans.local.")
    testbase.assert_equal(in_msg.authorities[0].name, "auth.local.")
    testbase.assert_equal(in_msg.additionals[0].name, "add.local.")
    return

if __name__ == "__main__":
    test_packet_splitting_correctly_preserves_records()
    test_packet_splitting_single_oversized_record()
    test_packet_splitting_mixed_types()
    test_packet_splitting_reverts_compression_state()
    test_packet_splitting_large_authority_record()
    test_packet_splitting_large_additional_record()
    test_packet_splitting_does_not_duplicate_questions()
    test_parsing_split_sections()
    print("All tests passed!")
