import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsflags import DEFAULT_DNS_FLAGS_QUERY
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from automojo.interop.protocols.dns.dnstext import DnsText


def test_read_ttl_as_unsigned() -> None:
    ttl_val = 0x80000000
    record = DnsText("example.local", DnsRecordType.TXT, DnsRecordClass.IN, ttl=ttl_val, text=b"dummy")
    out_msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
    out_msg.add_answer(record)
    packets = out_msg.packets()
    testbase.assert_equal(len(packets), 1)

    in_msg = DnsInboundMessage(packets[0])
    testbase.assert_equal(len(in_msg.answers), 1)
    testbase.assert_equal(in_msg.answers[0].ttl, ttl_val)
    return


def test_is_query_and_response() -> None:
    """Verify that query and response detection works."""
    # Build a simple query packet with one question
    header = (
        b"\x12\x34"  # id
        b"\x00\x00"  # flags - query
        b"\x00\x01"  # questions
        b"\x00\x00"  # answers
        b"\x00\x00"  # authorities
        b"\x00\x00"  # additionals
    )
    question = b"\x07example\x05local\x00" + b"\x00\x01" + b"\x00\x01"
    qpacket = header + question

    qmsg = DnsInboundMessage(qpacket)
    testbase.assert_equal(qmsg.is_query(), True)
    testbase.assert_equal(qmsg.is_response(), False)

    # Build a minimal response packet with one answer
    rheader = (
        b"\xab\xcd"  # id
        b"\x80\x00"  # flags - response (QR=1)
        b"\x00\x00"  # questions
        b"\x00\x01"  # answers
        b"\x00\x00"  # authorities
        b"\x00\x00"  # additionals
    )
    name = b"\x07example\x05local\x00"
    answer = (
        name
        + b"\x00\x01"  # type A
        + b"\x00\x01"  # class IN
        + b"\x00\x00\x00\x05"  # ttl
        + b"\x00\x04"  # length
        + b"\x01\x02\x03\x04"  # address
    )
    rpacket = rheader + answer

    rmsg = DnsInboundMessage(rpacket)
    testbase.assert_equal(rmsg.is_query(), False)
    testbase.assert_equal(rmsg.is_response(), True)
    return


def test_name_decoding_with_compression() -> None:
    """Ensure that compressed names are expanded correctly."""
    header = (
        b"\x00\x00"  # id
        b"\x00\x00"  # flags
        b"\x00\x00"  # questions
        b"\x00\x02"  # answers
        b"\x00\x00"  # authorities
        b"\x00\x00"  # additionals
    )
    name = b"\x07example\x05local\x00"
    ans1 = (
        name
        + b"\x00\x01"
        + b"\x00\x01"
        + b"\x00\x00\x00\x0a"
        + b"\x00\x04"
        + b"\x01\x02\x03\x04"
    )
    ans2 = (
        b"\xC0\x0c"  # pointer to first name
        + b"\x00\x01"
        + b"\x00\x01"
        + b"\x00\x00\x00\x14"
        + b"\x00\x04"
        + b"\x05\x06\x07\x08"
    )
    packet = header + ans1 + ans2
    msg = DnsInboundMessage(packet)
    testbase.assert_equal(len(msg.answers), 2)
    for ans in msg.answers:
        testbase.assert_equal(ans.name, "example.local.")
    return


def test_str_representation() -> None:
    """Ensure __str__ returns a formatted description."""
    packet = (
        b"\x00\x01"  # id
        b"\x00\x00"  # flags
        b"\x00\x00"  # questions
        b"\x00\x00"  # answers
        b"\x00\x00"  # authorities
        b"\x00\x00"  # additionals
    )
    msg = DnsInboundMessage(packet)
    srepr = str(msg)
    testbase.assert_equal(srepr.startswith("<DnsInboundMessage:"), True)
    testbase.assert_equal("id=" in srepr, True)
    return

