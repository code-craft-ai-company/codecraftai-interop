
import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsquestion import DnsQuestion
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass, DnsQr, DnsOpCode, DnsRespCode
from automojo.interop.protocols.dns.dnsflags import DnsFlags
import struct

def test_dns_question_preserves_qu_bit() -> None:
    """
    Test that the QU (Unicast Response) bit is preserved when writing a Question to a packet.
    """
    # Setup
    flags = DnsFlags(qr=DnsQr.Query, opcode=DnsOpCode.Query, aa=False, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)
    
    # Create Question with UNIQUE bit (QU)
    q_class_in = DnsRecordClass.IN | DnsRecordClass.UNIQUE
    q = DnsQuestion("qu-test.local.", DnsRecordType.A, q_class_in)
    
    msg.add_question(q)
    
    packets = msg.packets()
    testbase.assert_equal(len(packets), 1)

    p1 = packets[0]
    
    # Parse the packet to find the Question Section Class field.
    # Header: 12 bytes.
    # Name: "qu-test.local."
    # Labels: 
    #   7 'qu-test'
    #   5 'local'
    #   0
    # Total name length = 1 + 7 + 1 + 5 + 1 = 15 bytes.
    # QTYPE = 2 bytes.
    # QCLASS = 2 bytes.
    # Offset of QCLASS = 12 + 15 + 2 = 29.
    
    class_offset = 12 + 15 + 2
    
    # Verify we are at the right place manually roughly (sanity check)
    # The byte before QTYPE should be 0 (end of name)
    testbase.assert_equal(p1[12 + 15 - 1], 0)
    
    qclass = struct.unpack("!H", p1[class_offset:class_offset+2])[0]
    
    # Check if UNIQUE bit (0x8000) is set.
    # 0x8001 = 32769
    expected_class = DnsRecordClass.IN | DnsRecordClass.UNIQUE
    
    testbase.assert_equal(qclass, expected_class.value)
    return

if __name__ == "__main__":
    test_dns_question_preserves_qu_bit()
    print("All tests passed!")
