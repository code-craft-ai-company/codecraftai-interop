"""
    .. module:: dnsnaptr
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the :class:`DnsNaptr` object which represents a DNS NAPTR record.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import TYPE_CHECKING, Union

from ccai.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage


class DnsNaptr(DnsRecord):
    """A DNS Naming Authority Pointer (NAPTR) record."""

    def __init__(
        self,
        name: str,
        rtype: int,
        rclass: int,
        ttl: Union[float, int],
        order: int,
        preference: int,
        flags: str,
        services: str,
        regexp: str,
        replacement: str,
    ) -> None:
        """Constructs a DNS NAPTR record."""
        super().__init__(name, rtype, rclass, ttl)
        self._order = order
        self._preference = preference
        self._flags = flags
        self._services = services
        self._regexp = regexp
        self._replacement = replacement
        return

    @property
    def order(self) -> int:
        """Order value for this NAPTR record."""
        return self._order

    @property
    def preference(self) -> int:
        """Preference value for this NAPTR record."""
        return self._preference

    @property
    def flags(self) -> str:
        """Flags string."""
        return self._flags

    @property
    def services(self) -> str:
        """Service parameters for this record."""
        return self._services

    @property
    def regexp(self) -> str:
        """Regular expression rule."""
        return self._regexp

    @property
    def replacement(self) -> str:
        """Replacement domain name."""
        return self._replacement

    def write(self, out: "DnsOutboundMessage") -> None:
        """Used when constructing an outgoing packet."""
        out.write_short(self._order)
        out.write_short(self._preference)
        out.write_string(self._flags)
        out.write_string(self._services)
        out.write_string(self._regexp)
        out.write_name(self._replacement, suppress_compression=True)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """Tests equality across NAPTR fields."""
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = (
                self._order == other._order
                and self._preference == other._preference
                and self._flags == other._flags
                and self._services == other._services
                and self._regexp == other._regexp
                and self._replacement == other._replacement
            )
        return iseq

    def __ne__(self, other: DnsRecord) -> bool:
        """Non-equality test."""
        return not self.__eq__(other)

    def __str__(self) -> str:
        """String representation."""
        other = f"{self._replacement} {self._order} {self._preference} {self._flags} {self._services} {self._regexp}"
        strval = self.as_dns_string(other=other)
        return strval
