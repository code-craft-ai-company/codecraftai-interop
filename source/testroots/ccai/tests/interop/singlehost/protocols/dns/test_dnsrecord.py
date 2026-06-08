import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsrecord import DnsRecord
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from ccai.interop.protocols.dns import dnsrecord
from ccai.testbase.mocking import create_module_patch


def test_dnsrecord_rclass_equality():
    rec1 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)
    rec2 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.CH, ttl=10)
    testbase.assert_equal(rec1 == rec2, False)


def test_as_dns_string_and_str_include_ttl_values():
    """Verify as_dns_string and __str__ show TTL information."""

    # Make time deterministic
    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=0)
        rec = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=5000)
        sval = rec.as_dns_string("info")
    testbase.assert_equal(sval, "record[1,1,example.com]=10/5,info")

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=0)
        sval = str(rec)
    testbase.assert_equal(sval, "record[1,1,example.com]=10/10,None")


def test_get_remaining_ttl_and_expiration():
    """Ensure remaining TTL and expiration checks work."""

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=0)
        rec = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)

    testbase.assert_equal(rec.get_remaining_ttl(5000), 5)
    testbase.assert_equal(rec.is_expired(11000), True)
    testbase.assert_equal(rec.is_stale(6000), True)


def test_update_ttl_recomputes_markers():
    """Update TTL values from another record."""

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=0)
        rec1 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=5000)
        rec2 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=20)

    rec1.update_ttl(rec2)
    testbase.assert_equal(rec1.ttl, 20)
    testbase.assert_equal(rec1.get_remaining_ttl(5000), 20)


class DummyMsg:
    def __init__(self, answers):
        self.answers = answers


def test_suppressed_by_answer_and_message():
    """Check suppression logic using another record and message."""

    with create_module_patch(dnsrecord, "current_time_millis") as ctm:
        ctm.configure(return_value=0)
        rec1 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)

    rec2 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=6)
    rec3 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=4)

    testbase.assert_equal(rec1.suppressed_by_answer(rec2), True)
    testbase.assert_equal(rec1.suppressed_by_answer(rec3), False)

    msg = DummyMsg([rec2])
    testbase.assert_equal(rec1.suppressed_by(msg), True)
