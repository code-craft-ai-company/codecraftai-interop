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

class _BigRecord(DnsRecord):
    """Record that writes a large payload."""

    def __init__(self, size: int) -> None:
        super().__init__("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=10)
        self._size = size

    def write(self, out: DnsOutboundMessage) -> None:
        out.write(b"x" * self._size)
        return


def test_write_record_respects_size_limit() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    rec = _BigRecord(2000)
    start_size = msg.size
    res = msg._write_record(rec, 0)
    testbase.assert_equal(res, False)
    testbase.assert_equal(msg.size, start_size)
    return


def test_write_character_string_too_long() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    exc = None
    try:
        msg.write_character_string(b"z" * 256)
    except ValueError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, ValueError), True)
    return


def test_write_utf_too_long() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    exc = None
    try:
        msg._write_utf("z" * 65)
    except Exception as err:
        exc = err
    from automojo.interop.protocols.dns.exceptions import DnsNamePartTooLongError
    testbase.assert_equal(isinstance(exc, DnsNamePartTooLongError), True)
    return


def test_is_type_unique() -> None:
    testbase.assert_equal(DnsOutboundMessage.is_type_unique(DnsRecordType.TXT), True)
    testbase.assert_equal(DnsOutboundMessage.is_type_unique(DnsRecordType.SRV), True)
    testbase.assert_equal(DnsOutboundMessage.is_type_unique(DnsRecordType.A), True)
    testbase.assert_equal(DnsOutboundMessage.is_type_unique(DnsRecordType.AAAA), True)
    testbase.assert_equal(DnsOutboundMessage.is_type_unique(DnsRecordType.PTR), False)
    return


def test_str_includes_key_fields() -> None:
    msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    desc = str(msg)
    testbase.assert_expression(desc, r".*multicast=True.*")
    testbase.assert_expression(desc, r".*flags=.*")
    testbase.assert_expression(desc, r".*questions=.*")
    return
