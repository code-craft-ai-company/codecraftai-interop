import ccai.testbase as testbase

from ccai.interop.protocols.serial.tcpserialagent import TcpSerialAgent
from ccai.interop.aspects import AspectsCmd

class DummyTelnet:
    def __init__(self, prompt: bytes):
        self.prompt = prompt
        self.timeouts = []
        self.writes = []

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
        return


def test_open_session_uses_aspects() -> None:
    agent = TcpSerialAgent("dummy", port=1)
    aspects = AspectsCmd(connection_timeout=1)
    session = agent.open_session(aspects=aspects)
    testbase.assert_equal(session._aspects.connection_timeout, 1)
    return


def test_run_cmd_uses_timeout() -> None:
    agent = TcpSerialAgent("dummy", port=1)
    dummy = DummyTelnet(agent.SERIAL_PROMPT)
    agent._create_connection = lambda: dummy
    agent._restore_prompt = lambda _c: None

    aspects = AspectsCmd(inactivity_timeout=7)
    status, stdout, stderr = agent.run_cmd("cmd", aspects=aspects)

    testbase.assert_equal(dummy.timeouts, [7, 600, 7, 7])
    testbase.assert_equal(status, 0)
    testbase.assert_equal(stdout, "out")
    testbase.assert_equal(stderr, "")
    return
