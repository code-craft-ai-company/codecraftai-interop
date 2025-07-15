import automojo.testbase as testbase

from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsquestion import DnsQuestion
from automojo.interop.protocols.dns.dnsflags import DnsFlags
from automojo.interop.protocols.dns.dnspointer import DnsPointer
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from automojo.interop.protocols.dns.testmessages import DNS_QUERY_MESSAGE_IPV4_01, DNS_QUERY_MESSAGE_IPV6_01


def _ipv4_dns_payload():
    return DNS_QUERY_MESSAGE_IPV4_01.encode("latin1")[42:]


def _ipv6_dns_payload():
    return DNS_QUERY_MESSAGE_IPV6_01.encode("latin1")[62:]


def _build_test_packet():
    flags = DnsFlags.parse(0)
    msg = DnsOutboundMessage(flags)
    msg.add_question(DnsQuestion("_scanner._tcp.local.", DnsRecordType.PTR, DnsRecordClass.IN))
    msg.add_answer(
        DnsPointer(
            "_scanner._tcp.local.",
            DnsRecordType.PTR,
            DnsRecordClass.IN,
            ttl=4500,
            alias="HP Color LaserJet Pro M478f-9f [834BAB]._scanner._tcp.local.",
        )
    )
    packets = msg.packets()
    return packets[0]


def test_outbound_ipv4_serializes_to_test_message() -> None:
    pkt = _build_test_packet()
    testbase.assert_equal(pkt, _ipv4_dns_payload())
    return


def test_outbound_ipv6_serializes_to_test_message() -> None:
    pkt = _build_test_packet()
    testbase.assert_equal(pkt, _ipv6_dns_payload())
    return
