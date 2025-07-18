
import automojo.testbase as testbase
from automojo.credentials.sshcredential import SshCredential
from automojo.interop.protocols.ssh import sshbase
from automojo.interop.protocols.ssh.sshconst import TEMPLATE_COMMAND_SUCCESS, TEMPLATE_COMMAND_FAILURE
from automojo.interop.aspects import LoggingPattern
from automojo.testbase.mocking import create_class_patch, create_module_patch


class DummySsh(sshbase.SshBase):
    """Simple subclass that records commands."""
    def __init__(self, host: str, cred: SshCredential):
        super().__init__(host, cred)
        self.next_result = (0, "", "")
        self.command = None

    def run_cmd(self, command: str, exp_status=0, user=None, pty_params=None, aspects=None):
        self.command = command
        return self.next_result

def create_ssh():
    cred = SshCredential(identifier="dummy", categories=["ssh"], username="u", password="p")
    ssh = DummySsh("localhost", cred)
    return ssh


def test_load_key_file_prefers_rsa():
    ssh = create_ssh()
    with create_class_patch(sshbase.paramiko.RSAKey, "from_private_key_file") as rsa_patch, \
         create_class_patch(sshbase.paramiko.ECDSAKey, "from_private_key_file") as ecdsa_patch, \
         create_class_patch(sshbase.paramiko.Ed25519Key, "from_private_key_file") as ed_patch:
        rsa_patch.configure(return_value="rsa")
        ecdsa_patch.configure(side_effect=lambda *a, **k: (_ for _ in ()).throw(Exception("no")))
        ed_patch.configure(side_effect=lambda *a, **k: (_ for _ in ()).throw(Exception("no")))
        result = ssh._load_key_file("/tmp/key", "pw")
        rsa_patch.assert_called_once_with("/tmp/key", password="pw")
        testbase.assert_equal(ecdsa_patch.call_count, 0)
        testbase.assert_equal(ed_patch.call_count, 0)
        testbase.assert_equal(result, "rsa")
    return


def test_load_key_file_raises_when_all_fail():
    ssh = create_ssh()
    with create_class_patch(sshbase.paramiko.RSAKey, "from_private_key_file") as rsa_patch, \
         create_class_patch(sshbase.paramiko.ECDSAKey, "from_private_key_file") as ecdsa_patch, \
         create_class_patch(sshbase.paramiko.Ed25519Key, "from_private_key_file") as ed_patch:
        rsa_patch.configure(side_effect=lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
        ecdsa_patch.configure(side_effect=lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
        ed_patch.configure(side_effect=lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
        raised = False
        try:
            ssh._load_key_file("/tmp/key", "pw")
        except sshbase.ConfigurationError:
            raised = True
        testbase.assert_equal(raised, True)
    return


def test_log_command_result_success_and_failure():
    ssh = create_ssh()
    with create_module_patch(sshbase, "logger", recursive=True) as mock_logger:
        ssh._log_command_result("cmd", 0, "out", "", 0, LoggingPattern.ALL_RESULTS)
        exp = TEMPLATE_COMMAND_SUCCESS % (ssh._target_tag, "cmd", "out", "")
        mock_logger.info.assert_called_once_with(exp)
        ssh._log_command_result("cmd", 1, "o", "e", [0], LoggingPattern.ALL_RESULTS)
        mock_logger.error.assert_called_once_with(TEMPLATE_COMMAND_FAILURE % (ssh._target_tag, "cmd", "o", "e"))
    return


def test_verify_connectivity_true_and_false():
    ssh = create_ssh()
    ssh.next_result = (0, "Hello\n", "")
    vok = ssh.verify_connectivity()
    testbase.assert_equal(vok, True)
    testbase.assert_equal(ssh.command, "echo Hello")
    ssh.next_result = (1, "bad", "")
    vok = ssh.verify_connectivity()
    testbase.assert_equal(vok, False)
    return


def test_ssh_execute_command_passes_parameters():
    ssh = create_ssh()
    with create_module_patch(sshbase, "ssh_execute_command") as exec_patch:
        exec_patch.configure(return_value=(1, "o", "e"))
        result = ssh._ssh_execute_command("runner", "cmd", pty_params={"a":1}, inactivity_timeout=10, inactivity_interval=2, chunk_size=64)
        exec_patch.assert_called_once_with("runner", "cmd", pty_params={"a":1}, inactivity_timeout=10, inactivity_interval=2, chunk_size=64)
        testbase.assert_equal(result, (1, "o", "e"))
    return
