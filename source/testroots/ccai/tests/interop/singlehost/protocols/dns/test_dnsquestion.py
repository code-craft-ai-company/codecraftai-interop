import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsrecord import DnsRecord
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass


def test_properties_and_unique_masking() -> None:
    q = DnsQuestion("example.com", DnsRecordType.A, DnsRecordClass.IN | DnsRecordClass.UNIQUE)
    testbase.assert_equal(q.name, "example.com")
    testbase.assert_equal(q.rtype, DnsRecordType.A)
    testbase.assert_equal(q.rclass, DnsRecordClass.IN)
    testbase.assert_equal(q.unique, True)
    return


def test_answered_by_exact_and_any() -> None:
    rec = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)
    q_exact = DnsQuestion("example.com", DnsRecordType.A, DnsRecordClass.IN)
    q_any = DnsQuestion("example.com", DnsRecordType.ANY, DnsRecordClass.IN)
    testbase.assert_equal(q_exact.answered_by(rec), True)
    testbase.assert_equal(q_any.answered_by(rec), True)
    return


def test_as_query_bytes_and_dns_string() -> None:
    q = DnsQuestion("example.com", DnsRecordType.A, DnsRecordClass.IN)
    testbase.assert_equal(q.as_query_bytes(), b"question\x00A,IN,example.com")
    testbase.assert_equal(q.as_dns_string(), "question[A,IN,example.com]")

    q_unique = DnsQuestion("example.com", DnsRecordType.A, DnsRecordClass.IN | DnsRecordClass.UNIQUE)
    testbase.assert_equal(q_unique.as_query_bytes(), b"question\x00A,IN-unique,example.com")
    testbase.assert_equal(q_unique.as_dns_string(), "question[A,IN-unique,example.com]")
    return
