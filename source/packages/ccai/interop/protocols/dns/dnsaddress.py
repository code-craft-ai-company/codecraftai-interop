"""
    .. module:: dnsaddress
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsAddress record type.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TYPE_CHECKING

import socket

from ccai.networking.interfaces import is_ipv6_address

from ccai.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage


class DnsAddress(DnsRecord):
    """
        A DNS address record
    """

    def __init__(self, name: str, rtype: int, rclass: int, ttl: int, address: bytes, suppress_compression: bool = False) -> None:
        """
            Constructs a DNS address record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param address: Raw address bytes.
            :param suppress_compression: Optional parameter offering control over whether to suppress compression
                                        for the record.
        """

        DnsRecord.__init__(self, name, rtype, rclass, ttl, suppress_compression=suppress_compression)
        self._address = address
        return

    @property
    def address(self):
        """
            Returns the raw address bytes for this record.

            :returns: The raw address bytes for this record.
        """
        return self._address

    def write(self, out: "DnsOutboundMessage") -> None:
        """
            Used in constructing an outgoing packet

            :param out: The outbound DNS message to write the record to.
        """
        out.write(self._address)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """
            Tests equality by comparing address bytes.

            :param other: Record to compare against this one.

            :returns: ``True`` if records are equal.
        """
        # Call DnsRecord equality operator first because it can eliminate alot of equality checks early
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = self._address == other._address
        return iseq

    def __ne__(self, other: DnsRecord) -> bool:
        """
            Non-equality test.

            :param other: Record to compare against this one.

            :returns: ``True`` if the records are not equal.
        """
        isneq = not self.__eq__(other)
        return isneq

    def __str__(self) -> str:
        """
            String representation.

            :returns: Formatted string describing the address record.
        """
        strval = None

        try:
            strval = self.as_dns_string(
                socket.inet_ntop(
                    socket.AF_INET6 if is_ipv6_address(self._address) else socket.AF_INET, self._address
                )
            )
        except Exception:  # TODO stop catching all Exceptions
            strval = self.as_dns_string(str(self._address))

        return strval
