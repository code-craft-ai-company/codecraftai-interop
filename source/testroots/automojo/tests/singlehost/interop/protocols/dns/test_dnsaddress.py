import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsaddress import DnsAddress
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
import socket
import time
from automojo.testbase.mocking import create_module_patch

class DummyOut:
    def __init__(self):
        self.data = None

    def write(self, value):
        self.data = value

    def _write_utf(self, value):
        self.data = value


def test_write_passes_address():
    rec = DnsAddress("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=10, address=b"addr")
    dmy = DummyOut()
    rec.write(dmy)
    testbase.assert_equal(dmy.data, b"addr")
    return


def test_equality_and_inequality():
    addr1 = socket.inet_aton("1.1.1.1")
    rec1 = DnsAddress("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=5, address=addr1)
    rec2 = DnsAddress("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=5, address=addr1)
    addr2 = socket.inet_aton("1.1.1.2")
    rec3 = DnsAddress("example.com", DnsRecordType.A, DnsRecordClass.IN, ttl=5, address=addr2)
    testbase.assert_equal(rec1 == rec2, True)
    testbase.assert_equal(rec1 != rec2, False)
    testbase.assert_equal(rec1 == rec3, False)
    testbase.assert_equal(rec1 != rec3, True)
    return


def test_str_ipv4_and_ipv6():
    with create_module_patch(time, "time") as mock_time:
        mock_time.configure(return_value=0)
        ipv4 = DnsAddress(
            "example.com",
            DnsRecordType.A,
            DnsRecordClass.IN,
            ttl=10,
            address=socket.inet_aton("1.2.3.4"),
        )
        ipv6 = DnsAddress(
            "example.com",
            DnsRecordType.AAAA,
            DnsRecordClass.IN,
            ttl=10,
            address=socket.inet_pton(socket.AF_INET6, "2001:db8::1"),
        )
        testbase.assert_equal(str(ipv4), "record[1,1,example.com]=10/10,1.2.3.4")
        testbase.assert_equal(str(ipv6), "record[28,1,example.com]=10/10,2001:db8::1")
    return
