import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsrecord import DnsRecord
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass


def test_dnsrecord_rclass_equality():
    rec1 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10)
    rec2 = DnsRecord("example.com", DnsRecordType.A, DnsRecordClass.CH, ttl=10)
    testbase.assert_equal(rec1 == rec2, False)
