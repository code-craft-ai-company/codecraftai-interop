import socket
import threading

import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsserver import DnsServer
from ccai.networking import constants
from ccai.testbase.mocking import Mock, create_module_patch


def test_init_sets_endpoint_properties():
    server = DnsServer()
    testbase.assert_equal(server.svc_addr, constants.MDNS_GROUP_ADDR)
    testbase.assert_equal(server.svc_port, constants.MDNS_PORT)
    return


def test_wait_calls_shutdown_gate_when_running():
    server = DnsServer()
    server._running = True
    gate = Mock(recursive=True)
    server._shutdown_gate = gate
    server.wait(timeout=5)
    gate.wait.assert_called_once_with(5)
    return


def test_wait_does_not_call_shutdown_gate_when_not_running():
    server = DnsServer()
    server._running = False
    gate = Mock(recursive=True)
    server._shutdown_gate = gate
    server.wait(timeout=2)
    testbase.assert_equal(gate.wait.call_count, 0)
    return


def test_start_creates_and_runs_thread():
    server = DnsServer()

    def dummy_entry(gate):
        gate.set()
        return

    server._entry_thread_response = dummy_entry

    class DummyThread:
        def __init__(self, name, target, args):
            self.name = name
            self.target = target
            self.args = args
            self.daemon = False
            self.started = False

        def setDaemon(self, val):
            self.daemon = val

        def start(self):
            self.started = True
            self.target(*self.args)

    with create_module_patch(threading, "Thread") as mock_thread:
        mock_thread.configure(side_effect=lambda name, target, args: DummyThread(name, target, args))
        server.start()
        testbase.assert_equal(isinstance(server._thread_response, DummyThread), True)
        testbase.assert_equal(server._thread_response.daemon, True)
        testbase.assert_equal(server._thread_response.started, True)
    return


class RecordingSocket:
    """
        A datagram socket stand-in that records what is sent through it and whether it was closed.
    """

    def __init__(self):
        self.sent = []
        self.closed = False
        return

    def sendto(self, data, addr):
        self.sent.append((data, addr))
        return len(data)

    def close(self):
        self.closed = True
        return


def test_query_all_services_sends_a_dnssd_service_enumeration_query():
    """
        query_all_services multicasts a PTR question for the DNS-SD service type enumeration name to the
        server endpoint and closes its socket.
    """
    server = DnsServer()
    sock = RecordingSocket()
    server._create_query_socket = lambda: sock

    packets = server.query_all_services()

    testbase.assert_equal(sock.closed, True)
    testbase.assert_equal(len(sock.sent), 1)
    testbase.assert_equal(len(packets), 1)

    packet, addr = sock.sent[0]
    testbase.assert_equal(packet, packets[0])
    testbase.assert_equal(addr, (constants.MDNS_GROUP_ADDR, constants.MDNS_PORT))

    query = DnsInboundMessage(packet)
    testbase.assert_equal(query.is_query(), True)
    testbase.assert_equal(len(query.questions), 1)

    question = query.questions[0]
    testbase.assert_equal(question.name.rstrip("."), "_services._dns-sd._udp.local")
    testbase.assert_equal(question.rtype, DnsRecordType.PTR)
    testbase.assert_equal(question.rclass, DnsRecordClass.IN)
    return


def test_query_all_services_uses_the_domain_and_endpoint():
    """
        The enumeration name is built for the requested domain and sent to the endpoint the server was
        created with.
    """
    server = DnsServer(endpoint=("192.0.2.10", 5454))
    sock = RecordingSocket()
    server._create_query_socket = lambda: sock

    server.query_all_services(domain="example.org")

    packet, addr = sock.sent[0]
    testbase.assert_equal(addr, ("192.0.2.10", 5454))

    question = DnsInboundMessage(packet).questions[0]
    testbase.assert_equal(question.name.rstrip("."), "_services._dns-sd._udp.example.org")
    return


class FailingSendSocket(RecordingSocket):
    """
        A socket stand-in whose send fails.
    """

    def sendto(self, data, addr):
        raise OSError("network is unreachable")


def test_query_all_services_closes_the_socket_when_the_send_fails():
    """
        A failing send propagates to the caller and the socket is still closed.
    """
    server = DnsServer()
    sock = FailingSendSocket()
    server._create_query_socket = lambda: sock

    raised = None
    try:
        server.query_all_services()
    except OSError as xcpt:
        raised = xcpt

    testbase.assert_true(raised is not None, "the send error propagates")
    testbase.assert_equal(sock.closed, True)
    return


def test_create_query_socket_sends_from_the_server_port():
    """
        The query socket is bound to the server port with address reuse and the multicast DNS TTL, so the
        queries originate from the multicast DNS port and the answers are multicast to the group.
    """
    server = DnsServer()

    created = []

    class OptionSocket(RecordingSocket):
        def __init__(self, *args):
            super().__init__()
            self.args = args
            self.options = {}
            self.bound_to = None
            created.append(self)
            return

        def setsockopt(self, level, option, value):
            self.options[(level, option)] = value
            return

        def bind(self, addr):
            self.bound_to = addr
            return

    with create_module_patch(socket, "socket") as mock_socket:
        mock_socket.configure(side_effect=OptionSocket)
        sock = server._create_query_socket()

    testbase.assert_equal(len(created), 1)
    testbase.assert_true(sock is created[0], "the created socket is returned")
    testbase.assert_equal(sock.args, (socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP))
    testbase.assert_equal(sock.bound_to, ("0.0.0.0", constants.MDNS_PORT))
    testbase.assert_equal(sock.options[(socket.SOL_SOCKET, socket.SO_REUSEADDR)], 1)
    testbase.assert_equal(sock.options[(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL)], 255)
    testbase.assert_equal(sock.closed, False)
    return


def test_create_query_socket_on_a_platform_without_so_reuseport():
    """
        Windows has no socket.SO_REUSEPORT.  The query socket is still created and bound there, relying on
        SO_REUSEADDR alone to share the port.
    """
    server = DnsServer()

    class OptionSocket(RecordingSocket):
        def __init__(self, *args):
            super().__init__()
            self.options = {}
            self.bound_to = None
            return

        def setsockopt(self, level, option, value):
            self.options[(level, option)] = value
            return

        def bind(self, addr):
            self.bound_to = addr
            return

    had_reuseport = hasattr(socket, "SO_REUSEPORT")
    saved_reuseport = getattr(socket, "SO_REUSEPORT", None)
    if had_reuseport:
        delattr(socket, "SO_REUSEPORT")
    try:
        with create_module_patch(socket, "socket") as mock_socket:
            mock_socket.configure(side_effect=OptionSocket)
            sock = server._create_query_socket()
    finally:
        if had_reuseport:
            socket.SO_REUSEPORT = saved_reuseport

    testbase.assert_equal(sock.bound_to, ("0.0.0.0", constants.MDNS_PORT))
    testbase.assert_equal(sock.options[(socket.SOL_SOCKET, socket.SO_REUSEADDR)], 1)
    testbase.assert_equal(len(sock.options), 2)
    testbase.assert_equal(sock.closed, False)
    return
