import automojo.testbase as testbase
from automojo.interop.aspects import AspectsCmd
from automojo.testbase.mocking import create_module_patch

from automojo.interop.protocols.ssh import sshagent


class DummyCred:
    username = "u"
    password = "p"


class DummyClient:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True
        return


class DummyAgent(sshagent.SshAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []
        self.created = []

    def _create_client(self, session_user=None):
        self.calls.append(("create_client", session_user))
        cl = DummyClient()
        self.created.append(cl)
        return cl

    def _run_cmd(self, ssh_client, command, exp_status=0, user=None, pty_params=None, aspects=None):
        self.calls.append(("run_cmd", command, exp_status, user, pty_params, aspects))
        return 0, "stdout", "stderr"

    def _directory_exists(self, ssh_client, remotedir):
        self.calls.append(("dir_exists", remotedir))
        return True

    def _get_home_directory(self, aspects=None):
        self.calls.append(("get_home_directory", aspects))
        return "/home/u"

def test_open_session_passes_aspects():
    cred = DummyCred()
    agent = DummyAgent("127.0.0.1", cred)
    aspects = AspectsCmd(connection_timeout=5)

    class DummySession:
        def __init__(self, *args, **kwargs):
            DummySession.kwargs = kwargs

    with create_module_patch(sshagent, "SshSession") as mock_session:
        mock_session.configure(side_effect=lambda *a, **k: DummySession(*a, **k))
        sess = agent.open_session(aspects=aspects)
        testbase.assert_equal(isinstance(sess, DummySession), True)
        testbase.assert_equal(DummySession.kwargs["aspects"], aspects)
    return

def test_run_cmd_creates_and_closes_client():
    cred = DummyCred()
    agent = DummyAgent("127.0.0.1", cred)
    status, out, err = agent.run_cmd("cmd")

    testbase.assert_equal(agent.calls[0][0], "create_client")
    testbase.assert_equal(agent.calls[1][0], "run_cmd")
    testbase.assert_equal(status, 0)
    testbase.assert_equal(out, "stdout")
    testbase.assert_equal(err, "stderr")
    testbase.assert_equal(agent.created[0].closed, True)
    return

def test_run_cmd_uses_provided_client():
    cred = DummyCred()
    agent = DummyAgent("127.0.0.1", cred)
    client = DummyClient()
    status, out, err = agent.run_cmd("cmd", ssh_client=client)

    testbase.assert_equal(agent.calls[0][0], "run_cmd")
    testbase.assert_equal(client.closed, False)
    testbase.assert_equal(status, 0)
    testbase.assert_equal(out, "stdout")
    testbase.assert_equal(err, "stderr")
    return

def test_directory_exists_calls_underlying_and_closes():
    cred = DummyCred()
    agent = DummyAgent("127.0.0.1", cred)
    exists = agent.directory_exists("/tmp")

    testbase.assert_equal(agent.calls[0][0], "create_client")
    testbase.assert_equal(agent.calls[1], ("dir_exists", "/tmp"))
    testbase.assert_equal(exists, True)
    testbase.assert_equal(agent.created[0].closed, True)
    return

def test_get_home_directory_forwards_aspects():
    cred = DummyCred()
    agent = DummyAgent("127.0.0.1", cred)
    aspects = AspectsCmd()
    home = agent.get_home_directory(aspects=aspects)

    testbase.assert_equal(agent.calls, [("get_home_directory", aspects)])
    testbase.assert_equal(home, "/home/u")
    return
