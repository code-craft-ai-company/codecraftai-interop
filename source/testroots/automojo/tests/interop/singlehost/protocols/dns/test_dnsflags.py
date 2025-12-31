import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsflags import DnsFlags, DEFAULT_DNS_FLAGS_QUERY
from automojo.interop.protocols.dns.dnsconst import DnsQr, DnsOpCode, DnsRespCode


def test_flags_roundtrip() -> None:
    flags = DnsFlags(
        qr=DnsQr.Response,
        opcode=DnsOpCode.Status,
        aa=True,
        tc=False,
        rd=True,
        ra=False,
        rcode=DnsRespCode.Refused,
    )
    value = flags.flags()
    parsed = DnsFlags.parse(value)
    testbase.assert_equal(parsed.qr, flags.qr)
    testbase.assert_equal(parsed.opcode, flags.opcode)
    testbase.assert_equal(parsed.aa, flags.aa)
    testbase.assert_equal(parsed.tc, flags.tc)
    testbase.assert_equal(parsed.rd, flags.rd)
    testbase.assert_equal(parsed.ra, flags.ra)
    testbase.assert_equal(parsed.rcode, flags.rcode)
    testbase.assert_equal(parsed.z, flags.z)
    testbase.assert_equal(parsed.flags(), value)
    return


def test_default_flags_query_value() -> None:
    # DEFAULT_DNS_FLAGS_QUERY has Opcode=Query(0) and all other flags 0
    testbase.assert_equal(DEFAULT_DNS_FLAGS_QUERY.flags(), 0x0000)
    return


def test_dnsflags_repr() -> None:
    flags = DnsFlags(
        qr=DnsQr.Query,
        opcode=DnsOpCode.IQuery,
        aa=True,
        tc=True,
        rd=False,
        ra=True,
        rcode=DnsRespCode.FormatError,
    )
    expected = "DnsFlags(qr=0, opcode=1, aa=True, tc=True, rd=False, ra=True, rcode=1, z=0)"
    testbase.assert_equal(repr(flags), expected)
    return
