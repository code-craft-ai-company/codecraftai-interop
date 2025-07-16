"""
.. module:: testmessagesipv6
:platform: Darwin, Linux, Unix, Windows
:synopsis: Sample IPv6 DNS messages used for unit testing.

.. moduleauthor:: AutomationX
"""

__author__ = "AutomationX"

from automojo.interop.protocols.dns.dnsconst import (
    DnsRecordClass,
    DnsRecordType,
)
from automojo.interop.protocols.dns.dnsflags import DnsFlags
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsquestion import DnsQuestion
from automojo.interop.protocols.dns.dnspointer import DnsPointer
from automojo.interop.protocols.dns.dnsservice import DnsService
from automojo.interop.protocols.dns.dnstext import DnsText
from automojo.interop.protocols.dns.dnsaddress import DnsAddress


class _RawDnsAddress(DnsAddress):
    """Helper record used to emit raw address bytes."""

    def write(self, out: DnsOutboundMessage) -> None:  # noqa: D401 - Too simple
        """Write raw address bytes to the outbound message."""
        out.write(self._address)
        return


DNS_IPV6_QUERY_AAAA_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x1c\x00\x01"
DNS_IPV6_RESPONSE_AAAA_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x00\x3c\x00\x10\x26\x06\x28\x00\x02\x20\x00\x01\x02\x48\x18\x92\x00\x00\x00\x00"

DNS_IPV6_QUERY_CNAME_WWW = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x05\x00\x01"
DNS_IPV6_RESPONSE_CNAME_WWW = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03\x77\x77\x77\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x05\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x00\x3c\x00\x0d\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00"

DNS_IPV6_QUERY_MX_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x0f\x00\x01"
DNS_IPV6_RESPONSE_MX_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x0f\x00\x01\xc0\x0c\x00\x0f\x00\x01\x00\x00\x00\x3c\x00\x14\x00\x0a\x04\x6d\x61\x69\x6c\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00"

DNS_IPV6_QUERY_TXT_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x10\x00\x01"
DNS_IPV6_RESPONSE_TXT_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x10\x00\x01\xc0\x0c\x00\x10\x00\x01\x00\x00\x00\x3c\x00\x06\x05\x68\x65\x6c\x6c\x6f"

DNS_IPV6_QUERY_NS_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x02\x00\x01"
DNS_IPV6_RESPONSE_NS_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x02\x00\x01\xc0\x0c\x00\x02\x00\x01\x00\x00\x00\x3c\x00\x11\x03\x6e\x73\x31\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00"

DNS_IPV6_QUERY_SOA_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x06\x00\x01"
DNS_IPV6_RESPONSE_SOA_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x06\x00\x01\xc0\x0c\x00\x06\x00\x01\x00\x00\x00\x3c\x00\x3d\x03\x6e\x73\x31\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x0a\x68\x6f\x73\x74\x6d\x61\x73\x74\x65\x72\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x00\x00\x01\x00\x00\x1c\x20\x00\x00\x0e\x10\x00\x12\x75\x00\x00\x00\x0e\x10"

DNS_IPV6_QUERY_PTR_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x32\x01\x39\x01\x38\x01\x31\x01\x38\x01\x34\x01\x32\x01\x30\x01\x31\x01\x30\x01\x30\x01\x30\x01\x30\x01\x32\x01\x32\x01\x30\x01\x30\x01\x30\x01\x38\x01\x32\x01\x36\x01\x30\x01\x36\x01\x32\x03\x69\x70\x36\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01"
DNS_IPV6_RESPONSE_PTR_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x30\x01\x32\x01\x39\x01\x38\x01\x31\x01\x38\x01\x34\x01\x32\x01\x30\x01\x31\x01\x30\x01\x30\x01\x30\x01\x30\x01\x32\x01\x32\x01\x30\x01\x30\x01\x30\x01\x38\x01\x32\x01\x36\x01\x30\x01\x36\x01\x32\x03\x69\x70\x36\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01\xc0\x0c\x00\x0c\x00\x01\x00\x00\x00\x3c\x00\x0d\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00"

DNS_IPV6_QUERY_SRV_SIP = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04\x5f\x73\x69\x70\x04\x5f\x74\x63\x70\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x21\x00\x01"
DNS_IPV6_RESPONSE_SRV_SIP = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x04\x5f\x73\x69\x70\x04\x5f\x74\x63\x70\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x21\x00\x01\xc0\x0c\x00\x21\x00\x01\x00\x00\x00\x3c\x00\x1d\x00\x00\x00\x05\x13\xc4\x09\x73\x69\x70\x73\x65\x72\x76\x65\x72\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00"

DNS_IPV6_QUERY_NAPTR_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x23\x00\x01"
DNS_IPV6_RESPONSE_NAPTR_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x23\x00\x01\xc0\x0c\x00\x23\x00\x01\x00\x00\x00\x3c\x00\x2b\x00\x64\x00\x0a\x01\x55\x07\x45\x32\x55\x2b\x73\x69\x70\x1f\x21\x5e\x2e\x2a\x24\x21\x73\x69\x70\x3a\x69\x6e\x66\x6f\x40\x65\x78\x61\x6d\x70\x6c\x65\x2e\x63\x6f\x6d\x21\x00"

DNS_IPV6_QUERY_DS_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x2b\x00\x01"
DNS_IPV6_RESPONSE_DS_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x2b\x00\x01\xc0\x0c\x00\x2b\x00\x01\x00\x00\x00\x3c\x00\x18\x00\x01\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

DNS_IPV6_QUERY_DNSKEY_EXAMPLE = "\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x30\x00\x01"
DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE = "\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x30\x00\x01\xc0\x0c\x00\x30\x00\x01\x00\x00\x00\x3c\x00\x06\x01\x00\x03\x08\x01\x02"

DNS_IPV6_MULTI_QUERY_A_AAAA = "\x56\x78\x01\x00\x00\x02\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x01\x00\x01\x03\x77\x77\x77\x07\x65\x78\x61\x6d\x70\x6c\x65\x03\x63\x6f\x6d\x00\x00\x1c\x00\x01"


def builder_for_DNS_IPV6_QUERY_AAAA_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_AAAA_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.AAAA, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_AAAA_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_AAAA_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.AAAA, DnsRecordClass.IN))
    addr_bytes = bytes.fromhex("26062800022000010248189200000000")
    msg.add_answer(_RawDnsAddress("example.com.", DnsRecordType.AAAA, DnsRecordClass.IN, 60, addr_bytes))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_CNAME_WWW() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_CNAME_WWW`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("www.example.com.", DnsRecordType.CNAME, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_CNAME_WWW() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_CNAME_WWW`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("www.example.com.", DnsRecordType.CNAME, DnsRecordClass.IN))
    msg.add_answer(
        DnsPointer(
            "www.example.com.",
            DnsRecordType.CNAME,
            DnsRecordClass.IN,
            ttl=60,
            alias="example.com.",
        )
    )
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_MX_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_MX_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.MX, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_MX_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_MX_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.MX, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_TXT_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_TXT_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.TXT, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_TXT_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_TXT_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.TXT, DnsRecordClass.IN))
    msg.add_answer(DnsText("example.com.", DnsRecordType.TXT, DnsRecordClass.IN, 60, b"\x05hello"))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_NS_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_NS_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.NS, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_NS_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_NS_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.NS, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_SOA_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_SOA_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.SOA, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_SOA_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_SOA_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.SOA, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_PTR_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_PTR_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(
        DnsQuestion(
            "0.0.0.0.0.0.0.0.2.9.8.1.8.4.2.0.1.0.0.0.0.2.2.0.0.0.8.2.6.0.6.2.ip6.arpa.",
            DnsRecordType.PTR,
            DnsRecordClass.IN,
        )
    )
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_PTR_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_PTR_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(
        DnsQuestion(
            "0.0.0.0.0.0.0.0.2.9.8.1.8.4.2.0.1.0.0.0.0.2.2.0.0.0.8.2.6.0.6.2.ip6.arpa.",
            DnsRecordType.PTR,
            DnsRecordClass.IN,
        )
    )
    msg.add_answer(
        DnsPointer(
            "0.0.0.0.0.0.0.0.2.9.8.1.8.4.2.0.1.0.0.0.0.2.2.0.0.0.8.2.6.0.6.2.ip6.arpa.",
            DnsRecordType.PTR,
            DnsRecordClass.IN,
            ttl=60,
            alias="example.com.",
        )
    )
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_SRV_SIP() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_SRV_SIP`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("_sip._tcp.example.com.", DnsRecordType.SRV, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_SRV_SIP() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_SRV_SIP`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("_sip._tcp.example.com.", DnsRecordType.SRV, DnsRecordClass.IN))
    msg.add_answer(
        DnsService(
            "_sip._tcp.example.com.",
            DnsRecordType.SRV,
            DnsRecordClass.IN,
            ttl=60,
            priority=0,
            weight=5,
            port=5060,
            server="sipserver.example.com.",
        )
    )
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_NAPTR_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_NAPTR_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.NAPTR, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_NAPTR_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_NAPTR_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.NAPTR, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_DS_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_DS_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.DS, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_DS_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_DS_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.DS, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_QUERY_DNSKEY_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_QUERY_DNSKEY_EXAMPLE`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.DNSKEY, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE() -> bytes:
    """Builder for :data:`DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE`."""

    flags = DnsFlags.parse(0x8180)
    msg = DnsOutboundMessage(flags, id=0x1234, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("example.com.", DnsRecordType.DNSKEY, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt


def builder_for_DNS_IPV6_MULTI_QUERY_A_AAAA() -> bytes:
    """Builder for :data:`DNS_IPV6_MULTI_QUERY_A_AAAA`."""

    flags = DnsFlags.parse(0x0100)
    msg = DnsOutboundMessage(flags, id=0x5678, multicast=False, use_compression=False)
    msg.add_question(DnsQuestion("www.example.com.", DnsRecordType.A, DnsRecordClass.IN))
    msg.add_question(DnsQuestion("www.example.com.", DnsRecordType.AAAA, DnsRecordClass.IN))
    packets = msg.packets()
    pkt = packets[0]

    return pkt
