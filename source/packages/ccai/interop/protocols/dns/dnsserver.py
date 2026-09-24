"""
    .. module:: dnsserver
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the :class:`DnsServer` class which implements a DNS server.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import List

import socket
import threading

from ccai.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType
from ccai.interop.protocols.dns.dnsflags import DEFAULT_DNS_FLAGS_QUERY
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from ccai.networking.constants import MDNS_GROUP_ADDR, MDNS_PORT


# The DNS-SD service type enumeration name (RFC 6763 section 9); a PTR query for it in a domain lists
# the service types advertised in that domain.
DNSSD_SERVICES_ENUMERATION_PREFIX = "_services._dns-sd._udp"

# Multicast DNS messages are sent with an IP TTL of 255 (RFC 6762 section 11).
MDNS_MULTICAST_TTL = 255

class DnsServer:
    """
        A DNS server
    """

    def __init__(self, endpoint=(MDNS_GROUP_ADDR, MDNS_PORT) ) -> None:
        """
            Initializes the DNS server instance.

            :param endpoint: Tuple containing address and port for the service.
        """

        self._svc_addr, self._svc_port = endpoint
        
        self._thread_response = None
        self._running = False
        self._shutdown_gate = threading.Event()
        self._shutdown_gate.set()
        return

    @property
    def svc_addr(self):
        """
            Address this DNS server is bound to.
        """
        return self._svc_addr

    @property
    def svc_port(self):
        """
            Port this DNS server listens on.
        """
        return self._svc_port

    def start(self):
        """
            Starts the responder thread for the server.
        """

        sgate = threading.Event()
        sgate.clear()

        self._thread_response = threading.Thread(name="dns-responder", target=self._entry_thread_response, args=[sgate])
        self._thread_response.setDaemon(True)
        self._thread_response.start()

        sgate.wait()

        return
    
    def query_all_services(self, domain: str = "local") -> List[bytes]:
        """
            Queries all services by broadcasting a DNS-SD request: a PTR question for the DNS-SD service type
            enumeration name ``_services._dns-sd._udp.<domain>`` (RFC 6763 section 9) is sent to the server
            endpoint.  The query is sent from the server port so responders multicast their answers to the
            group (RFC 6762 section 6.7), where the responder thread of this server receives them.

            :param domain: The DNS domain whose service types are enumerated.

            :returns: The packets that were sent.
        """

        svc_type = f"{DNSSD_SERVICES_ENUMERATION_PREFIX}.{domain}"

        question = DnsQuestion(svc_type, DnsRecordType.PTR, DnsRecordClass.IN)

        query_msg = DnsOutboundMessage(DEFAULT_DNS_FLAGS_QUERY)
        query_msg.add_question(question)

        msg_packets = query_msg.packets()

        sock = self._create_query_socket()
        try:
            for packet in msg_packets:
                sock.sendto(packet, (self._svc_addr, self._svc_port))
        finally:
            sock.close()

        return msg_packets

    def _create_query_socket(self) -> socket.socket:
        """
            Creates the UDP socket used to send queries.  It is bound to the server port, shared with the
            responder thread, so the queries originate from the multicast DNS port.

            :returns: The bound datagram socket.
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        bound = False
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MDNS_MULTICAST_TTL)
            sock.bind(("0.0.0.0", self._svc_port))
            bound = True
        finally:
            if not bound:
                # Do not leak the socket when it cannot be set up, the error propagates to the caller.
                sock.close()

        return sock

    def wait(self, timeout=None):
        """
            Blocks until the server stops running or until *timeout* expires.

            :param timeout: Number of seconds to wait before giving up.
        """

        if self._running:
            self._shutdown_gate.wait(timeout)

    def _entry_thread_response(self, sgate: threading.Event):
        """
            The entry point for monitor thread.  The monitor thread sets up monitoring on all interfaces.

            :param sgate: The startup gate that is used to indicate to the thread spinning up the coordinator
                          that the monitor thread has started.
        """
        multicast_address = MDNS_GROUP_ADDR
        multicast_port = MDNS_PORT

        try:
            self._running = True
            self._shutdown_gate.clear()

            # Set the start gate to allow the thread spinning us up to continue
            sgate.set()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            try:
                # Make sure other Automation processes can also bind to the DNS address and port
                # so they can also get responses.
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                # Set us up to be a member of the group, this allows us to receive all the packets
                # that are sent to the group
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast_address) + socket.inet_aton('0.0.0.0'))

                sock.bind((multicast_address, multicast_port))

                while self._running:
                    msg_data, addr = sock.recvfrom(1024)

                    reader = DnsInboundMessage(msg_data)

                    print(reader)

            finally:
                sock.close()

        finally:
            self._shutdown_gate.set()

        return
