import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsflags import DEFAULT_DNS_FLAGS_QUERY
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from automojo.interop.protocols.dns.dnstext import DnsText


def test_read_ttl_as_unsigned() -> None:
    ttl_val = 0x80000000
    record = DnsText("example.local", DnsRecordType.TXT, DnsRecordClass.IN, ttl=ttl_val, text=b"dummy")
    out_msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    out_msg.add_answer(record)
    packets = out_msg.packets()
    testbase.assert_equal(len(packets), 1)

    in_msg = DnsInboundMessage(packets[0])
    testbase.assert_equal(len(in_msg.answers), 1)
    testbase.assert_equal(in_msg.answers[0].ttl, ttl_val)
    return

