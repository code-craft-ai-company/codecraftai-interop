"""
    .. module:: dnsmailexchange
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsMailExchange record type.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import TYPE_CHECKING

from automojo.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage


class DnsMailExchange(DnsRecord):
    """
        A DNS mail exchange (MX) record.
    """

    def __init__(self, name: str, rtype: int, rclass: int, ttl: int, preference: int, exchange: str) -> None:
        """
            Constructs a DNS mail exchange record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param preference: Preference value for the mail exchange server.
            :param exchange: Hostname of the mail exchange server.
        """
        super().__init__(name, rtype, rclass, ttl)
        self._preference = preference
        self._exchange = exchange
        return

    @property
    def preference(self) -> int:
        """
            Preference value for the mail server.

            :returns: Preference integer.
        """
        return self._preference

    @property
    def exchange(self) -> str:
        """
            Hostname of the mail exchange server.

            :returns: Mail server hostname.
        """
        return self._exchange

    def write(self, out: "DnsOutboundMessage") -> None:
        """
            Used in constructing an outgoing packet.

            :param out: The outbound DNS message to write the record to.
        """
        out.write_short(self._preference)
        out.write_name(self._exchange)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """
            Tests equality on preference and exchange.

            :param other: Record to compare against this one.

            :returns: ``True`` if records are equal.
        """
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = self._preference == other._preference and self._exchange == other._exchange
        return iseq

    def __ne__(self, other: DnsRecord) -> bool:
        """
            Non-equality test.

            :param other: Record to compare against this one.

            :returns: ``True`` if the records are not equal.
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
            String representation.

            :returns: Formatted string representing this mail exchange record.
        """
        other = f"{self._exchange} {self._preference}"
        strval = self.as_dns_string(other=other)
        return strval
