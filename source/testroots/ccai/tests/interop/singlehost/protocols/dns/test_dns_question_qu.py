
import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass, DnsQr, DnsOpCode, DnsRespCode
from ccai.interop.protocols.dns.dnsflags import DnsFlags

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

    inbound = DnsInboundMessage(p1)
    testbase.assert_equal(len(inbound.questions), 1)

    parsed_question = inbound.questions[0]
    testbase.assert_equal(parsed_question.name, "qu-test.local.")
    testbase.assert_equal(parsed_question.rtype, DnsRecordType.A)
    testbase.assert_equal(parsed_question.rclass, DnsRecordClass.IN)
    testbase.assert_equal(parsed_question.unique, True)
    return

if __name__ == "__main__":
    test_dns_question_preserves_qu_bit()
    print("All tests passed!")
