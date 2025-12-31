import automojo.testbase as testbase
from automojo.interop.protocols.serial.tcpserialagent import TcpSerialSession
from automojo.interop.aspects import AspectsCmd


class DummyTelnet:
    def __init__(self, prompt: bytes):
        self.prompt = prompt
        self.timeouts = []
        self.writes = []
        self.closed = False

    def write(self, data: bytes):
        self.writes.append(data)

    def read_until(self, prompt: bytes, timeout: float | None = None):
        self.timeouts.append(timeout)
        if len(self.timeouts) == 1:
            return b""
        if len(self.timeouts) == 2:
            return b"cmd\nout\n" + self.prompt
        if len(self.timeouts) == 3:
            return b"echo $?\n0\n" + self.prompt
        if len(self.timeouts) == 4:
            return b"cat $TNSTDERR\n" + self.prompt
        return self.prompt

    def close(self):
        self.closed = True
        return


def test_session_run_cmd_uses_timeout() -> None:
    session = TcpSerialSession("dummy", port=1)
    dummy = DummyTelnet(session.SERIAL_PROMPT)
    called = []

    def create_conn():
        called.append(1)
        return dummy

    session._create_connection = create_conn
    aspects = AspectsCmd(inactivity_timeout=5)
    status, stdout, stderr = session.run_cmd("cmd", aspects=aspects)

    testbase.assert_equal(called, [1])
    testbase.assert_equal(dummy.timeouts, [5, 600, 5, 5])
    testbase.assert_equal(status, 0)
    testbase.assert_equal(stdout, "out")
    testbase.assert_equal(stderr, "")
    return


def test_session_close_closes_owned_connection() -> None:
    session = TcpSerialSession("dummy", port=1)
    dummy = DummyTelnet(session.SERIAL_PROMPT)
    session._telnet_conn = dummy
    calls = []
    session._restore_prompt = lambda conn: calls.append(conn)

    session.close()

    testbase.assert_equal(calls, [dummy])
    testbase.assert_equal(dummy.closed, True)
    return


def test_session_close_shared_does_not_close() -> None:
    basis = TcpSerialSession("dummy", port=1)
    dummy = DummyTelnet(basis.SERIAL_PROMPT)
    basis._telnet_conn = dummy
    session = TcpSerialSession("dummy", port=1, session_basis=basis)
    session._telnet_conn = dummy
    calls = []
    session._restore_prompt = lambda conn: calls.append(conn)

    session.close()

    testbase.assert_equal(calls, [])
    testbase.assert_equal(dummy.closed, False)
    return


def test_session_exit_calls_close_and_returns_false() -> None:
    session = TcpSerialSession("dummy", port=1)
    calls = []
    session.close = lambda: calls.append(1)
    handled = session.__exit__(None, None, None)

    testbase.assert_equal(calls, [1])
    testbase.assert_equal(handled, False)
    return
