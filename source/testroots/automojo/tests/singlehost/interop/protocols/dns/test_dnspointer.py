import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnspointer import DnsPointer
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
import time
from automojo.testbase.mocking import create_module_patch


class DummyOut:
    def __init__(self):
        self.received = []

    def write_name(self, name: str, force_no_compression: bool) -> None:
        self.received.append((name, force_no_compression))


def test_write_calls_write_name() -> None:
    rec = DnsPointer(
        "_service._tcp.local",
        DnsRecordType.PTR,
        DnsRecordClass.IN,
        ttl=10,
        alias="alias.local",
    )
    dummy = DummyOut()
    rec.write(dummy)
    testbase.assert_equal(dummy.received, [("alias.local", False)])
    return


def test_equality_and_inequality() -> None:
    rec1 = DnsPointer(
        "_service._tcp.local",
        DnsRecordType.PTR,
        DnsRecordClass.IN,
        ttl=10,
        alias="alias.local",
    )
    rec2 = DnsPointer(
        "_service._tcp.local",
        DnsRecordType.PTR,
        DnsRecordClass.IN,
        ttl=10,
        alias="alias.local",
    )
    rec3 = DnsPointer(
        "_service._tcp.local",
        DnsRecordType.PTR,
        DnsRecordClass.IN,
        ttl=10,
        alias="other.local",
    )
    testbase.assert_equal(rec1 == rec2, True)
    testbase.assert_equal(rec1 != rec2, False)
    testbase.assert_equal(rec1 == rec3, False)
    testbase.assert_equal(rec1 != rec3, True)
    return


def test_str_includes_alias_and_ttl() -> None:
    with create_module_patch(time, "time") as mock_time:
        mock_time.configure(return_value=0)
        rec = DnsPointer(
            "_service._tcp.local",
            DnsRecordType.PTR,
            DnsRecordClass.IN,
            ttl=10,
            alias="alias.local",
        )
        sval = str(rec)
        testbase.assert_equal(
            sval,
            "record[12,1,_service._tcp.local]=10/10,alias.local",
        )
    return
