import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnstext import DnsText
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from unittest import mock


class DummyOut:
    def __init__(self):
        self.calls = []

    def write_character_string(self, buf):
        self.calls.append(buf)


def test_write_calls_write_character_string():
    rec = DnsText("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=10, text=b"payload")
    dummy = DummyOut()
    rec.write(dummy)
    testbase.assert_equal(dummy.calls, [b"payload"])
    return


def test_equality_and_inequality():
    rec1 = DnsText("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=5, text=b"text")
    rec2 = DnsText("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=5, text=b"text")
    rec3 = DnsText("example.com", DnsRecordType.TXT, DnsRecordClass.IN, ttl=5, text=b"other")
    testbase.assert_equal(rec1 == rec2, True)
    testbase.assert_equal(rec1 != rec2, False)
    testbase.assert_equal(rec1 == rec3, False)
    testbase.assert_equal(rec1 != rec3, True)
    return


def test_str_truncates_long_text():
    with mock.patch("time.time", return_value=0):
        rec = DnsText(
            "example.com",
            DnsRecordType.TXT,
            DnsRecordClass.IN,
            ttl=10,
            text=b"abcdefghijklmnop",
        )
        testbase.assert_equal(str(rec), "record[16,1,example.com]=10/10,abcdefg...")
    return
