import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnshostinfo import DnsHostInfo
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass

class DummyOut:
    def __init__(self):
        self.calls = []
    def write(self, buf):
        self.calls.append(("write", buf))
    def write_character_string(self, buf):
        self.calls.append(("write_character_string", buf))

def test_write_calls_outbound_methods():
    rec = DnsHostInfo("host.local", DnsRecordType.HINFO, DnsRecordClass.IN, ttl=10, cpu="x86", os="Linux")
    dummy = DummyOut()
    rec.write(dummy)
    testbase.assert_equal(dummy.calls[0], ("write", b"x86"))
    testbase.assert_equal(dummy.calls[1], ("write_character_string", b"Linux"))


def test_equality_and_inequality():
    rec1 = DnsHostInfo("host.local", DnsRecordType.HINFO, DnsRecordClass.IN, ttl=10, cpu="x86", os="Linux")
    rec2 = DnsHostInfo("host.local", DnsRecordType.HINFO, DnsRecordClass.IN, ttl=10, cpu="x86", os="Linux")
    rec3 = DnsHostInfo("host.local", DnsRecordType.HINFO, DnsRecordClass.IN, ttl=10, cpu="arm", os="Linux")
    testbase.assert_equal(rec1 == rec2, True)
    testbase.assert_equal(rec1 != rec2, False)
    testbase.assert_equal(rec1 == rec3, False)
    testbase.assert_equal(rec1 != rec3, True)


def test_string_contains_cpu_and_os():
    rec = DnsHostInfo("host.local", DnsRecordType.HINFO, DnsRecordClass.IN, ttl=10, cpu="x86", os="Linux")
    sval = str(rec)
    testbase.assert_equal("x86 Linux" in sval, True)
