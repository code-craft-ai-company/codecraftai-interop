import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage, DnsPacketBuilderState
from automojo.interop.protocols.dns.dnsflags import DEFAULT_DNS_FLAGS_QUERY
from automojo.interop.protocols.dns.dnsrecord import DnsRecord
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass

class _DummyRecord(DnsRecord):
    """A simple DNS record used for testing."""
    def __init__(self) -> None:
        super().__init__("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=10)

    def write(self, out: DnsOutboundMessage) -> None:
        out._write_utf("dummy")
        return

def test_write_record_stops_after_finished() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    msg.packets()
    testbase.assert_equal(msg.state, DnsPacketBuilderState.Finished)
    rec = _DummyRecord()
    res = msg._write_record(rec, 0)
    testbase.assert_equal(res, False)
    return


def test_write_string_accepts_str() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    msg.write_string("foo")
    testbase.assert_equal(msg.data[-2:], [b"\x03", b"foo"])
    return
