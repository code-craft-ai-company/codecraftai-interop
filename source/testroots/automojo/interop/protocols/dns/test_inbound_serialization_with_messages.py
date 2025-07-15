import automojo.testbase as testbase

from automojo.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from automojo.interop.protocols.dns.testmessages import DNS_QUERY_MESSAGE_IPV4_01, DNS_QUERY_MESSAGE_IPV6_01


def _ipv4_dns_payload():
    return DNS_QUERY_MESSAGE_IPV4_01.encode("latin1")[42:]


def _ipv6_dns_payload():
    return DNS_QUERY_MESSAGE_IPV6_01.encode("latin1")[62:]


def _validate_message(pkt: bytes) -> None:
    msg = DnsInboundMessage(pkt)
    testbase.assert_equal(len(msg.questions), 1)
    testbase.assert_equal(len(msg.answers), 1)

    q = msg.questions[0]
    testbase.assert_equal(q.name, "_scanner._tcp.local.")
    testbase.assert_equal(q.rtype, DnsRecordType.PTR)
    testbase.assert_equal(q.rclass, DnsRecordClass.IN)

    a = msg.answers[0]
    testbase.assert_equal(a.alias, "HP Color LaserJet Pro M478f-9f [834BAB]._scanner._tcp.local.")
    testbase.assert_equal(a.ttl, 4500)
    return


def test_inbound_ipv4_deserializes_test_message() -> None:
    _validate_message(_ipv4_dns_payload())
    return


def test_inbound_ipv6_deserializes_test_message() -> None:
    _validate_message(_ipv6_dns_payload())
    return
