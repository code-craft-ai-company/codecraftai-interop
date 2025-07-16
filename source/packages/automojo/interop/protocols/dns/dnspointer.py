"""
    .. module:: dnspointer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsPointer which represents a DNS record pointer.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from automojo.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage

class DnsPointer(DnsRecord):
    """
        A DNS pointer record
    """

    def __init__(self, name: str, rtype: int, rclass: int, ttl: int, alias: str, *, suppress_compression: bool = False) -> None:
        """
            Constructs a DNS pointer record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param alias: Alias name for the record.
            :param suppress_compression: Optional parameter offering control over whether to suppress compression
                                        for the record.
        """
        DnsRecord.__init__(self, name, rtype, rclass, ttl, suppress_compression=suppress_compression)
        self._alias = alias
        self._suppress_compression = suppress_compression
        return

    @property
    def alias(self):
        """
            The alias name pointed to by this record.

            :returns: Alias value as a string.
        """
        return self._alias

    @property
    def suppress_compression(self) -> bool:
        """Indicates if the alias name should be written without compression."""

        return self._suppress_compression

    def write(self, out: 'DnsOutboundMessage') -> None:
        """
            Used in constructing an outgoing packet

            :param out: The outbound DNS message to write the record to.
        """
        out.write_name(self._alias, suppress_compression=self._suppress_compression)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """
            Tests equality on alias.

            :param other: Record to compare against this one.

            :returns: ``True`` if records are equal.
        """
        # Call DnsRecord equality operator first because it can eliminate alot of equality checks early
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = self._alias == other._alias
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

            :returns: Formatted string representing the pointer record.
        """
        other = self._alias
        strval = self.as_dns_string(other=other)
        return strval
