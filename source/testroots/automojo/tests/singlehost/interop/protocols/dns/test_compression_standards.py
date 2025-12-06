
import automojo.testbase as testbase

from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsflags import DnsFlags, DnsQr, DnsOpCode, DnsRespCode
from automojo.interop.protocols.dns.dnsquestion import DnsQuestion
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass

def test_compression_case_sensitivity():
    """
    Verify that DNS name compression is case-insensitive as per RFC 1035.
    """
    flags = DnsFlags(qr=DnsQr.Query, opcode=DnsOpCode.Query, aa=False, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
    msg = DnsOutboundMessage(flags)

    # Use a name that definitely has mixed case
    name1 = "Example.com"
    name2 = "example.com"

    q1 = DnsQuestion(name1, DnsRecordType.A, DnsRecordClass.IN)
    q2 = DnsQuestion(name2, DnsRecordType.A, DnsRecordClass.IN)

    msg.add_question(q1)
    msg.add_question(q2)

    packets = msg.packets()
    data = packets[0]

    # Calculate expected offsets
    # Header: 12 bytes
    # Q1:
    # Label "Example": 1 byte len + 7 bytes = 8
    # Label "com": 1 byte len + 3 bytes = 4
    # Terminator: 1 byte = 1
    # Type: 2 bytes
    # Class: 2 bytes
    # Total Q1 name len = 8 + 4 + 1 = 13.
    # Total Q1 len = 13 + 4 = 17.

    q1_end = 12 + 17 # 29

    if len(data) <= q1_end:
        testbase.assert_true(False, "Packet too short to contain second question.")

    byte_at_start_of_q2 = data[q1_end]

    # Check for pointer (0xC0)
    # RFC 1035 Section 4.1.4: "a pointer to a prior occurrence of the same name."
    # "Example.com" and "example.com" are the same name.
    is_pointer = (byte_at_start_of_q2 & 0xC0) == 0xC0

    testbase.assert_true(is_pointer, "DNS compression should be case-insensitive. 'example.com' should be compressed as a pointer to 'Example.com'.")

    return
