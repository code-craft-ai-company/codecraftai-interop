"""
    .. module:: dnssoa
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the :class:`DnsSoa` object which represents a DNS SOA record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import TYPE_CHECKING, Union

from ccai.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage


class DnsSoa(DnsRecord):
    """A DNS Start of Authority (SOA) record."""

    def __init__(
        self,
        name: str,
        rtype: int,
        rclass: int,
        ttl: Union[float, int],
        mname: str,
        rname: str,
        serial: int,
        refresh: int,
        retry: int,
        expire: int,
        minimum: int,
    ) -> None:
        """Constructs a DNS SOA record."""
        super().__init__(name, rtype, rclass, ttl)
        self._mname = mname
        self._rname = rname
        self._serial = serial
        self._refresh = refresh
        self._retry = retry
        self._expire = expire
        self._minimum = minimum
        return

    @property
    def mname(self) -> str:
        """Primary name server for the zone."""
        return self._mname

    @property
    def rname(self) -> str:
        """Responsible party for the zone."""
        return self._rname

    def write(self, out: "DnsOutboundMessage") -> None:
        """Used when constructing an outgoing packet."""
        out.write_name(self._mname, suppress_compression=True)
        out.write_name(self._rname, suppress_compression=True)
        out.write_int(self._serial)
        out.write_int(self._refresh)
        out.write_int(self._retry)
        out.write_int(self._expire)
        out.write_int(self._minimum)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """Tests equality across SOA fields."""
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = (
                self._mname == other._mname
                and self._rname == other._rname
                and self._serial == other._serial
                and self._refresh == other._refresh
                and self._retry == other._retry
                and self._expire == other._expire
                and self._minimum == other._minimum
            )
        return iseq

    def __ne__(self, other: DnsRecord) -> bool:
        """Non-equality test."""
        return not self.__eq__(other)

    def __str__(self) -> str:
        """String representation."""
        other = f"{self._mname} {self._rname}"
        strval = self.as_dns_string(other=other)
        return strval
