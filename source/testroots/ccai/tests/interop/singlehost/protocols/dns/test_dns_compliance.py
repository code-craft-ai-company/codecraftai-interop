
import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsflags import DnsFlags
from ccai.interop.protocols.dns.dnsconst import DnsQr, DnsRespCode

def test_response_flags_compliance():
    """
    Verifies that DNS flags are parsed correctly according to RFC 1035.

    Standard Response Flags (0x8180):
    QR=1 (Response)
    Opcode=0 (Query)
    AA=0
    TC=0
    RD=1 (Recursion Desired)
    RA=1 (Recursion Available)
    Z=0
    RCODE=0 (No Error)

    Binary (Big Endian): 1000 0001 1000 0000
    Hex: 0x8180
    """

    flags_int = 0x8180
    flags = DnsFlags.parse(flags_int)

    testbase.assert_equal(flags.qr, DnsQr.Response)
    testbase.assert_equal(flags.rcode, DnsRespCode.NoError)
    testbase.assert_equal(flags.rd, True)
    testbase.assert_equal(flags.ra, True)
    testbase.assert_equal(flags.opcode, 0)

    # Also verify the reverse direction
    reconstructed = flags.flags()
    testbase.assert_equal(reconstructed, flags_int)

    return

def test_query_flags_compliance():
    """
    Verifies that a standard query flag set is parsed correctly.

    Standard Query with Recursion Desired (0x0100):
    QR=0 (Query)
    Opcode=0
    RD=1
    Other=0

    Binary: 0000 0001 0000 0000
    Hex: 0x0100
    """

    flags_int = 0x0100
    flags = DnsFlags.parse(flags_int)

    testbase.assert_equal(flags.qr, DnsQr.Query)
    testbase.assert_equal(flags.rd, True)
    testbase.assert_equal(flags.opcode, 0)
    testbase.assert_equal(flags.ra, False)

    reconstructed = flags.flags()
    testbase.assert_equal(reconstructed, flags_int)

    return
