import automojo.testbase as testbase
from automojo.interop.protocols.dns import dnsconst


def test_basic_constants_and_formats() -> None:
    testbase.assert_equal(dnsconst.DNS_SIZE_SIGNED_CHAR, 1)
    testbase.assert_equal(dnsconst.DNS_SIZE_SIGNED_SHORT, 2)
    testbase.assert_equal(dnsconst.DNS_SIZE_SIGNED_INTEGER, 4)

    testbase.assert_equal(dnsconst.DNS_SIZE_UNSIGNED_CHAR, 1)
    testbase.assert_equal(dnsconst.DNS_SIZE_UNSIGNED_SHORT, 2)
    testbase.assert_equal(dnsconst.DNS_SIZE_UNSIGNED_INTEGER, 4)

    testbase.assert_equal(dnsconst.DNS_PACKET_HEADER_SIZE, 12)
    testbase.assert_equal(dnsconst.DNS_RECEIVE_BUFFER, 4096)

    testbase.assert_equal(dnsconst.DNS_PACK_FORMAT_SHORT, "!H")
    testbase.assert_equal(dnsconst.DNS_PACK_FORMAT_INTEGER, "!I")
    return


def test_enum_values() -> None:
    testbase.assert_equal(dnsconst.DnsLiftimePercent.Expired, 100)
    testbase.assert_equal(dnsconst.DnsLiftimePercent.Stale, 50)
    testbase.assert_equal(dnsconst.DnsLiftimePercent.Refresh, 75)

    testbase.assert_equal(dnsconst.DnsQuestionType.QU, 1)
    testbase.assert_equal(dnsconst.DnsQuestionType.QM, 2)

    record_class_expected = {
        "IN": 1,
        "CS": 2,
        "CH": 3,
        "HS": 4,
        "NONE": 254,
        "ANY": 255,
        "MASK": 0x7FFF,
        "UNIQUE": 0x8000,
    }
    for name, value in record_class_expected.items():
        testbase.assert_equal(getattr(dnsconst.DnsRecordClass, name), value)

    record_type_expected = {
        "A": 1,
        "NS": 2,
        "MD": 3,
        "MF": 4,
        "CNAME": 5,
        "SOA": 6,
        "MB": 7,
        "MG": 8,
        "MR": 9,
        "NULL": 10,
        "WKS": 11,
        "PTR": 12,
        "HINFO": 13,
        "MINFO": 14,
        "MX": 15,
        "TXT": 16,
        "RP": 17,
        "AFSDB": 18,
        "SIG": 24,
        "KEY": 25,
        "AAAA": 28,
        "LOC": 29,
        "SRV": 33,
        "NAPTR": 35,
        "KX": 36,
        "CERT": 37,
        "DNAME": 39,
        "APL": 42,
        "DS": 43,
        "SSHFP": 44,
        "IPSECKEY": 45,
        "RRSIG": 46,
        "NSEC": 47,
        "DNSKEY": 48,
        "DHCID": 49,
        "NSEC3": 50,
        "NSEC3PARAM": 51,
        "TLSA": 52,
        "SMIMEA": 53,
        "HIP": 55,
        "CDS": 59,
        "CDNSKEY": 60,
        "OPENPGPKEY": 61,
        "CSYNC": 62,
        "ZONEMD": 63,
        "SVCB": 64,
        "HTTPS": 65,
        "EUI48": 108,
        "EUI64": 109,
        "TKEY": 249,
        "TSIG": 250,
        "AXFR": 252,
        "MAILB": 253,
        "MAILA": 254,
        "ANY": 255,
        "URI": 256,
        "CAA": 257,
        "TA": 32768,
        "DLV": 32769,
    }
    for name, value in record_type_expected.items():
        testbase.assert_equal(getattr(dnsconst.DnsRecordType, name), value)

    testbase.assert_equal(dnsconst.DnsQr.Query, 0)
    testbase.assert_equal(dnsconst.DnsQr.Response, 1)

    opcode_expected = {
        "Query": 0,
        "IQuery": 1,
        "Status": 2,
        "Notify": 4,
        "Update": 5,
    }
    for name, value in opcode_expected.items():
        testbase.assert_equal(getattr(dnsconst.DnsOpCode, name), value)

    resp_expected = {
        "NoError": 0,
        "FormatError": 1,
        "ServerError": 2,
        "NameError": 3,
        "Refused": 5,
        "NameExistsError": 6,
        "RRExistsError": 7,
        "NonAuthoritative": 8,
        "NotInZoneError": 9,
    }
    for name, value in resp_expected.items():
        testbase.assert_equal(getattr(dnsconst.DnsRespCode, name), value)
    return


def test_additional_constants() -> None:
    testbase.assert_equal(dnsconst.EXPIRE_FULL_TIME_PERCENT, 100)
    testbase.assert_equal(dnsconst.EXPIRE_STALE_TIME_PERCENT, 50)
    testbase.assert_equal(dnsconst.EXPIRE_REFRESH_TIME_PERCENT, 75)

    testbase.assert_equal(dnsconst.HAS_A_TO_Z.pattern, r"[A-Za-z]")
    testbase.assert_equal(dnsconst.HAS_ONLY_A_TO_Z_NUM_HYPHEN.pattern, r"^[A-Za-z0-9\-]+$")
    testbase.assert_equal(dnsconst.HAS_ONLY_A_TO_Z_NUM_HYPHEN_UNDERSCORE.pattern, r"^[A-Za-z0-9\-\_]+$")
    testbase.assert_equal(dnsconst.HAS_ASCII_CONTROL_CHARS.pattern, r"[\x00-\x1f\x7f]")

    testbase.assert_equal(dnsconst.MAX_MSG_TYPICAL, 1460)
    testbase.assert_equal(dnsconst.MAX_MSG_ABSOLUTE, 8966)

    testbase.assert_equal(dnsconst.DNS_COMP_MASK, 0xC0)
    testbase.assert_equal(dnsconst.DNS_OFFSET_MASK, 0x3F)

    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.AIRTUNES, "AirTunes Remote Audio")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.AIRPLAY, "_airplay._tcp")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.MICROSOFT_WINDOWS_NETWORK, "Microsoft Windows Network")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.SFTP, "SFTP File Transfer")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.SONOS, "_sonos._tcp")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.SPOTIFY_CONNECT, "_spotify-connect._tcp")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.SSH, "SSH Remote Terminal")
    testbase.assert_equal(dnsconst.DnsKnownServiceTypes.VNC, "VNC Remote Access")
    return
