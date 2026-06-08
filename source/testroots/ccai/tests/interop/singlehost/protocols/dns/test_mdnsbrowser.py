import ccai.testbase as testbase
from ccai.interop.protocols.dns.mdnsbrowser import MdnsBrowser
from ccai.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from ccai.testbase.mocking import create_class_patch


class DummySocket:
    def __init__(self):
        self.sent = []

    def sendto(self, data, addr):
        self.sent.append((data, addr))


def test_discover_services_sends_packets():
    browser = MdnsBrowser()
    browser._running = True

    dummy_socket = DummySocket()
    browser._get_search_socket = lambda: dummy_socket

    with create_class_patch(DnsOutboundMessage, "packets") as mock_packets:
        mock_packets.configure(return_value=[b"p1", b"p2"])
        browser.discover_services(["_http._tcp.local"])

    testbase.assert_equal(len(dummy_socket.sent), 2)
    for sent, expected in zip(dummy_socket.sent, [b"p1", b"p2"]):
        packet, addr = sent
        testbase.assert_equal(packet, expected)
        testbase.assert_equal(addr, (browser._multicast_address, browser._multicast_port))

