"""
    .. module:: dnstext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsText objec which reprsents a DNS text record type.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from automojo.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage

class DnsText(DnsRecord):
    """
        A DNS text record
    """

    def __init__(self, name: str, rtype: int, rclass: int, ttl: int, text: bytes) -> None:
        """
            Constructs a DNS text record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param text: Text payload as bytes.
        """
        assert isinstance(text, (bytes, type(None)))
        DnsRecord.__init__(self, name, rtype, rclass, ttl)
        self._text = text

    @property
    def text(self) -> str:
        """
            Raw text payload associated with the record.

            :returns: Byte string of the text data.
        """
        return self._text

    def write(self, out: 'DnsOutboundMessage') -> None:
        """
            Used in constructing an outgoing packet

            :param out: The outbound DNS message to write the record to.
        """
        out.write_character_string(self._text)

    def __eq__(self, other: DnsRecord) -> bool:
        """
            Tests equality on text.

            :param other: Record to compare against this one.

            :returns: ``True`` if records are equal.
        """
        # Call DnsRecord equality operator first because it can eliminate alot of equality checks early
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = self._text == other._text
        return iseq

    def __ne__(self, other: DnsRecord) -> bool:
        """
            Non-equality test.

            :param other: Record to compare against this one.

            :returns: ``True`` if the records are not equal.
        """
        isne = not self.__eq__(other)
        return isne

    def __str__(self) -> str:
        """
            String representation.

            :returns: Formatted string representing this text record.
        """
        strval = None

        txt_str = str(self._text, "utf-8", "replace")
        if len(txt_str) > 10:
            txt_str = txt_str[:7] + "..."

        strval = self.as_dns_string(txt_str)

        return strval
