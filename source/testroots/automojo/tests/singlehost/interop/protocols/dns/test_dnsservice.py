import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsservice import DnsService
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
import time
from automojo.testbase.mocking import create_module_patch


class DummyOut:
    def __init__(self):
        self.calls = []

    def write_short(self, value):
        self.calls.append(("write_short", value))

    def write_name(self, name):
        self.calls.append(("write_name", name))


def test_write_calls_outbound_methods():
    rec = DnsService(
        "svc.local",
        DnsRecordType.SRV,
        DnsRecordClass.IN,
        ttl=10,
        priority=5,
        weight=2,
        port=80,
        server="server.local",
    )
    dummy = DummyOut()
    rec.write(dummy)
    testbase.assert_equal(
        dummy.calls,
        [
            ("write_short", 5),
            ("write_short", 2),
            ("write_short", 80),
            ("write_name", "server.local"),
        ],
    )
    return


def test_equality_and_inequality():
    rec1 = DnsService(
        "svc.local",
        DnsRecordType.SRV,
        DnsRecordClass.IN,
        ttl=10,
        priority=5,
        weight=2,
        port=80,
        server="server.local",
    )
    rec2 = DnsService(
        "svc.local",
        DnsRecordType.SRV,
        DnsRecordClass.IN,
        ttl=20,
        priority=5,
        weight=2,
        port=80,
        server="server.local",
    )
    rec3 = DnsService(
        "svc.local",
        DnsRecordType.SRV,
        DnsRecordClass.IN,
        ttl=10,
        priority=5,
        weight=2,
        port=81,
        server="server.local",
    )
    testbase.assert_equal(rec1 == rec2, True)
    testbase.assert_equal(rec1 != rec2, False)
    testbase.assert_equal(rec1 == rec3, False)
    testbase.assert_equal(rec1 != rec3, True)
    return


def test_str_contains_all_fields():
    with create_module_patch(time, "time") as mock_time:
        mock_time.configure(return_value=0)
        rec = DnsService(
            "svc.local",
            DnsRecordType.SRV,
            DnsRecordClass.IN,
            ttl=10,
            priority=5,
            weight=2,
            port=80,
            server="server.local",
        )
        sval = str(rec)
        expected = "record[33,1,svc.local]=10/10,server.local 80 5 2"
        testbase.assert_equal(sval, expected)
    return
