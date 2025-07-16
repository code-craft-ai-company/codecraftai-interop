import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsserver import DnsServer
from automojo.networking import constants
from automojo.testbase.mocking import Mock, create_module_patch
import threading


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
