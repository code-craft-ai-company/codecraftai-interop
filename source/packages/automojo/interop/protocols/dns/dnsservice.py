"""
    .. module:: dnsservice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the :class:`DnsService` object which represents a DNS service record.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Union, TYPE_CHECKING

import threading

from automojo.interop.protocols.dns.dnsrecord import DnsRecord

if TYPE_CHECKING:
    from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage

class DnsService(DnsRecord):
    """
        A DNS service record
    """

    def __init__(self, name: str, rtype: int, rclass: int, ttl: Union[float, int], priority: int,
                 weight: int, port: int, server: str, suppress_compression: bool = True) -> None:
        """
            Constructs a DNS service record.

            :param name: Record name.
            :param rtype: Record type.
            :param rclass: Record class.
            :param ttl: Time-to-live for the record.
            :param priority: Service priority.
            :param weight: Service weight.
            :param port: Service port number.
            :param server: Hostname providing the service.
            :param suppress_compression: Optional parameter offering control over whether to suppress compression
                                        for the record.  Default is true for SRV records
        """
        DnsRecord.__init__(self, name, rtype, rclass, ttl, suppress_compression=suppress_compression)
        self._priority = priority
        self._weight = weight
        self._port = port
        self._server = server

        self._thread_response = None
        self._running = False
        self._shutdown_gate = threading.Event()
        self._shutdown_gate.set()
        return

    @property
    def port(self):
        """
            TCP/UDP port number of the service.

            :returns: Port as an integer.
        """
        return self._port

    @property
    def priority(self):
        """
            Service priority value used when multiple records exist.

            :returns: Priority value.
        """
        return self._priority

    @property
    def server(self):
        """
            Hostname providing the service.

            :returns: Server host name.
        """
        return self._server

    @property
    def weight(self):
        """
            Service weight used for load balancing.

            :returns: Weight value.
        """
        return self._weight
    
    def write(self, out: 'DnsOutboundMessage') -> None:
        """
            Used in constructing an outgoing packet

            :param out: The outbound DNS message to write the record to.
        """
        out.write_short(self._priority)
        out.write_short(self._weight)
        out.write_short(self._port)
        out.write_name(self._server, suppress_compression=self._suppress_compression)
        return

    def __eq__(self, other: DnsRecord) -> bool:
        """
            Tests equality on priority, weight, port and server.

            :param other: Record to compare against this one.

            :returns: ``True`` if records are equal.
        """
        # Call DnsRecord equality operator first because it can eliminate alot of equality checks early
        iseq = False
        if DnsRecord.__eq__(self, other):
            iseq = self._priority == other._priority and self._weight == other._weight and self._port == other._port and self._server == other._server
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

            :returns: String describing the service record.
        """
        other = f"{self._server} {self._port} {self._priority} {self._weight}"
        strval = self.as_dns_string(other=other)
        return strval
