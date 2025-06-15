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

    def __init__(self, name: str, rtype: int, rclass: int, ttl: int, alias: str) -> None:
        """
            Constructs a DNS pointer record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param alias: Alias name for the record.
        """
        DnsRecord.__init__(self, name, rtype, rclass, ttl)
        self._alias = alias
        return

    @property
    def alias(self):
        """
            The alias name pointed to by this record.

            :returns: Alias value as a string.
        """
        return self._alias

    def write(self, out: 'DnsOutboundMessage') -> None:
        """
            Used in constructing an outgoing packet

            :param out: The outbound DNS message to write the record to.
        """
        out.write_name(self._alias)
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
