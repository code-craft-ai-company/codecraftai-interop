import ccai.testbase as testbase
from ccai.credentials.sshcredential import SshCredential
from ccai.interop.protocols.ssh.sshsession import SshSession
from ccai.interop.protocols.ssh.sshconst import INTERACTIVE_PROMPT
from ccai.interop.aspects import AspectsCmd
from ccai.interop.protocols.ssh.sshbase import SshBase
from ccai.interop.protocols.ssh import sshsession
from ccai.testbase.mocking import create_class_patch, create_module_patch
import paramiko
import socket


class DummyClient:
    def __init__(self, transport=None):
        self.transport = transport
        self.closed = False

    def get_transport(self):
        return self.transport

    def close(self):
        self.closed = True
        return


class DummyTransport:
    def __init__(self, channel):
        self.channel = channel
        self.open_calls = []

    def is_active(self):
        return True

    def open_session(self, timeout=None):
        self.open_calls.append(timeout)
        return self.channel


class DummyBuffer:
    def __init__(self):
        self.calls = 0

    def read(self, _size, _timeout):
        self.calls += 1
        raise paramiko.buffered_pipe.PipeTimeout()


class DummyChannel:
    def __init__(self):
        self.in_buffer = DummyBuffer()
        self.in_stderr_buffer = DummyBuffer()
        self.calls = []

    def get_pty(self, **kwargs):
        self.calls.append(("get_pty", kwargs))

    def invoke_shell(self):
        self.calls.append(("invoke_shell",))

    def sendall(self, data):
        self.calls.append(("sendall", data))


def make_session(interactive=False, basis=None):
    cred = SshCredential(identifier="id", categories=["ssh"], username="u", password="p")
    with create_module_patch(socket, "gethostbyname") as gh:
        gh.configure(return_value="127.0.0.1")
        sess = SshSession("host", cred, interactive=interactive, basis_session=basis)
    return sess


def test_enter_non_interactive_sets_runner() -> None:
    session = make_session()
    dummy = DummyClient()
    calls = []
    session._create_client = lambda: (calls.append(1) or dummy)

    result = session.__enter__()

    testbase.assert_equal(calls, [1])
    testbase.assert_equal(result, session)
    testbase.assert_equal(session._ssh_client, dummy)
    testbase.assert_equal(session._ssh_runner, dummy)
    return


def test_enter_interactive_uses_channel() -> None:
    chan = DummyChannel()
    trans = DummyTransport(chan)
    client = DummyClient(trans)
    session = make_session(interactive=True)
    session._create_client = lambda: client

    session.__enter__()

    testbase.assert_equal(session._ssh_runner, chan)
    testbase.assert_equal(trans.open_calls, [session._aspects.inactivity_timeout])
    expected = [
        ("get_pty", {}),
        ("invoke_shell",),
        ("sendall", f"export PS1={INTERACTIVE_PROMPT}\n"),
    ]
    testbase.assert_equal(chan.calls, expected)
    return


def test_close_closes_owned_client() -> None:
    session = make_session()
    client = DummyClient()
    session._ssh_client = client

    session.close()

    testbase.assert_equal(client.closed, True)
    return


def test_close_shared_does_not_close() -> None:
    basis = make_session()
    client = DummyClient()
    basis._ssh_client = client
    session = make_session(basis=basis)
    session._ssh_client = client

    session.close()

    testbase.assert_equal(client.closed, False)
    return


def test_exit_calls_close_and_returns_false() -> None:
    session = make_session()
    calls = []
    session.close = lambda: calls.append(1)

    handled = session.__exit__(None, None, None)

    testbase.assert_equal(calls, [1])
    testbase.assert_equal(handled, False)
    return


def test_run_cmd_delegates_to__run_cmd() -> None:
    session = make_session()
    session._ssh_runner = object()
    called = []

    def run(runner, command, exp_status=0, user=None, pty_params=None, aspects=None):
        if aspects is None:
            aspects = session._aspects
        called.append((runner, command, exp_status, user, pty_params, isinstance(aspects, AspectsCmd)))
        return 0, "out", "err"

    session._run_cmd = run
    status, stdout, stderr = session.run_cmd("cmd", user="u")

    testbase.assert_equal(status, 0)
    testbase.assert_equal(stdout, "out")
    testbase.assert_equal(stderr, "err")
    runner, command, exp_status, user, pty_params, aspects_is_cmd = called[0]
    testbase.assert_equal(runner, session._ssh_runner)
    testbase.assert_equal(command, "cmd")
    testbase.assert_equal(exp_status, 0)
    testbase.assert_equal(user, "u")
    testbase.assert_equal(pty_params, None)
    testbase.assert_equal(aspects_is_cmd, True)
    return


def test_directory_methods_delegate_to_base() -> None:
    session = make_session()
    session._ssh_client = object()
    calls = []
    session._directory = lambda c, p: calls.append(("dir", c, p)) or {}
    session._directory_exists = lambda c, p: calls.append(("exists", c, p)) or True
    session._directory_tree = lambda c, p, depth=1: calls.append(("tree", c, p, depth)) or {}
    session._file_exists = lambda c, p: calls.append(("fexists", c, p)) or False
    session._file_pull = lambda c, rp, lp: calls.append(("pull", c, rp, lp))
    session._file_push = lambda c, lp, rp: calls.append(("push", c, lp, rp))
    session._get_home_directory = lambda aspects=None: "home"

    session.directory("/tmp")
    session.directory_exists("/tmp")
    session.directory_tree("/tmp", depth=2)
    session.file_exists("/tmp/f")
    session.file_pull("/tmp/f", "/l")
    session.file_push("/l", "/tmp/f")
    home = session.get_home_directory()

    testbase.assert_equal(home, "home")
    expected_calls = [
        ("dir", session._ssh_client, "/tmp"),
        ("exists", session._ssh_client, "/tmp"),
        ("tree", session._ssh_client, "/tmp", 2),
        ("fexists", session._ssh_client, "/tmp/f"),
        ("pull", session._ssh_client, "/tmp/f", "/l"),
        ("push", session._ssh_client, "/l", "/tmp/f"),
    ]
    testbase.assert_equal(calls, expected_calls)
    return


def test_open_session_with_basis_session() -> None:
    base = make_session()
    aspects = AspectsCmd(connection_timeout=1)
    with create_module_patch(socket, "gethostbyname") as gh:
        gh.configure(return_value="127.0.0.1")
        session = base.open_session(pty_params={"x": 1}, interactive=True, basis_session=base, aspects=aspects)

    testbase.assert_equal(session._host, base._host)
    testbase.assert_equal(session._basis_session, base)
    testbase.assert_equal(session._pty_params, {"x": 1})
    testbase.assert_equal(session._interactive, True)
    testbase.assert_equal(session._aspects.connection_timeout, 1)
    return


def test_create_client_uses_basis() -> None:
    basis = make_session()
    dummy = DummyClient(DummyTransport(DummyChannel()))
    basis._ssh_client = dummy
    session = make_session(basis=basis)

    client = session._create_client()

    testbase.assert_equal(client, dummy)
    return


def test_create_client_calls_base() -> None:
    session = make_session()
    dummy = DummyClient()
    called = []

    def base_create(*_args, **kwargs):
        session_user = kwargs.get("session_user")
        called.append(session_user)
        return dummy

    with create_class_patch(SshBase, "_create_client") as cp:
        cp.configure(side_effect=base_create)
        client = session._create_client()

    testbase.assert_equal(client, dummy)
    testbase.assert_equal(called, [None])
    return


def test_ssh_execute_command_uses_interactive_helpers() -> None:
    session = make_session(interactive=True)
    chan = object()
    with create_module_patch(sshsession, "ssh_execute_command_in_channel") as ceic:
        with create_module_patch(sshsession, "ssh_execute_command") as ce:
            ceic.configure(return_value=(0, "out", ""))
            ce.configure(return_value=(1, "", ""))
            status, stdout, _ = session._ssh_execute_command(chan, "cmd")
    testbase.assert_equal(status, 0)
    testbase.assert_equal(stdout, "out")
    return


def test_ssh_execute_command_non_interactive() -> None:
    session = make_session(interactive=False)
    client = object()
    with create_module_patch(sshsession, "ssh_execute_command_in_channel") as ceic:
        with create_module_patch(sshsession, "ssh_execute_command") as ce:
            ce.configure(return_value=(1, "out", ""))
            ceic.configure(return_value=(0, "", ""))
            status, stdout, _ = session._ssh_execute_command(client, "cmd")
    testbase.assert_equal(status, 1)
    testbase.assert_equal(stdout, "out")
    return
