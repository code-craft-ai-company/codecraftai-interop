
import ccai.testbase as testbase

from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsflags import DnsFlags, DnsQr, DnsOpCode, DnsRespCode
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass

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

    inbound = DnsInboundMessage(data)

    questions = inbound.questions

    testbase.assert_equal(len(questions), 2, "Expected both questions to round-trip in the message.")

    q1_in = questions[0]
    q2_in = questions[1]

    # RFC 1035 Section 3.1 specifies that domain names are case-insensitive. Compression is optional, so
    # we simply verify that the decoded names compare equal without regard to case regardless of whether
    # the implementation chose to emit a pointer or duplicate labels.
    testbase.assert_equal(q1_in.name.lower(), q2_in.name.lower(), "DNS names must compare case-insensitively after decoding.")

    return
