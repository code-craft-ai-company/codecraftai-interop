"""
    SSH integration tests for the ``ssh-address-plane-awareness`` feature.

    These tests cover :meth:`SshBase.connect` — the classmethod that
    resolves a dial target (either from a literal ``host`` or from a
    ``device``'s :class:`IDeviceAddressSet`) and then constructs the SSH
    context.
"""

import ccai.testbase as testbase

from ccai.credentials.sshcredential import SshCredential
from ccai.errors.exceptions import SemanticError

from ccai.interfaces.addressplane import AddressPlane, DeviceAddressSetSnapshot

from ccai.interop.protocols.ssh import sshbase
from ccai.interop.protocols.ssh.exceptions import SSHAddressPlaneUnavailableError
from ccai.testbase.mocking import create_module_patch


class DummySsh(sshbase.SshBase):
    """Concrete subclass used to construct SshBase for tests."""
    def run_cmd(self, command, exp_status=0, user=None, pty_params=None, aspects=None):
        return (0, "", "")


class DummyDevice:
    """Device wrapper exposing ``addresses()`` and a ``name`` attribute."""
    def __init__(self, *, name, address_set):
        self.name = name
        self._address_set = address_set
        return

    def addresses(self):
        return self._address_set


def _cred():
    rtnval = SshCredential(identifier="dummy", categories=["ssh"], username="u", password="p")
    return rtnval


def test_connect_with_literal_host_ignores_plane():
    cred = _cred()
    ssh = DummySsh.connect(host="localhost", primary_credential=cred)
    testbase.assert_equal(ssh.host, "localhost")
    return


def test_connect_with_host_and_device_raises_semantic():
    cred = _cred()
    snap = DeviceAddressSetSnapshot(public_address="1.2.3.4")
    device = DummyDevice(name="dev-a", address_set=snap)
    raised = False
    try:
        DummySsh.connect(host="localhost", device=device, primary_credential=cred)
    except SemanticError:
        raised = True
    testbase.assert_equal(raised, True)
    return


def test_connect_without_host_or_device_raises_semantic():
    cred = _cred()
    raised = False
    try:
        DummySsh.connect(primary_credential=cred)
    except SemanticError:
        raised = True
    testbase.assert_equal(raised, True)
    return


def test_connect_default_plane_uses_public_address():
    cred = _cred()
    snap = DeviceAddressSetSnapshot(public_address="127.0.0.1", private_address="10.0.0.1")
    device = DummyDevice(name="dev-a", address_set=snap)
    ssh = DummySsh.connect(device=device, primary_credential=cred)
    testbase.assert_equal(ssh.host, "127.0.0.1")
    return


def test_connect_overlay_plane_uses_overlay_address():
    cred = _cred()
    # Use 127.0.0.1 for the overlay value since SshBase.__init__ calls socket.gethostbyname.
    snap = DeviceAddressSetSnapshot(public_address="1.1.1.1", overlay_address="127.0.0.1")
    device = DummyDevice(name="dev-a", address_set=snap)
    ssh = DummySsh.connect(device=device, primary_credential=cred, address_plane=AddressPlane.OVERLAY)
    testbase.assert_equal(ssh.host, "127.0.0.1")
    return


def test_connect_falls_through_to_first_available():
    cred = _cred()
    snap = DeviceAddressSetSnapshot(private_address="127.0.0.1")
    device = DummyDevice(name="dev-a", address_set=snap)
    ssh = DummySsh.connect(device=device, primary_credential=cred,
                           address_plane=AddressPlane.PUBLIC,
                           fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY])
    testbase.assert_equal(ssh.host, "127.0.0.1")
    return


def test_connect_no_plane_available_raises():
    cred = _cred()
    snap = DeviceAddressSetSnapshot()
    device = DummyDevice(name="dev-empty", address_set=snap)
    raised = False
    try:
        DummySsh.connect(device=device, primary_credential=cred,
                         address_plane=AddressPlane.PUBLIC,
                         fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY])
    except SSHAddressPlaneUnavailableError as err:
        raised = True
        msg = str(err)
        testbase.assert_equal("dev-empty" in msg, True)
    testbase.assert_equal(raised, True)
    return


def test_connect_without_primary_credential_raises_semantic():
    raised = False
    try:
        DummySsh.connect(host="localhost")
    except SemanticError:
        raised = True
    testbase.assert_equal(raised, True)
    return


def test_connect_logs_plane_choice_and_skips():
    cred = _cred()
    snap = DeviceAddressSetSnapshot(private_address="127.0.0.1")
    device = DummyDevice(name="dev-logged", address_set=snap)

    with create_module_patch(sshbase, "logger", recursive=True) as mock_logger:
        DummySsh.connect(device=device, primary_credential=cred,
                         address_plane=AddressPlane.PUBLIC,
                         fallback_planes=[AddressPlane.PRIVATE])

        info_hit = False
        for call in mock_logger.info.call_args_list:
            rendered = repr(call)
            if "dev-logged" in rendered and "PRIVATE" in rendered and "127.0.0.1" in rendered:
                info_hit = True
                break
        testbase.assert_equal(info_hit, True)

        warn_hit = False
        for call in mock_logger.warning.call_args_list:
            rendered = repr(call)
            if "dev-logged" in rendered and "PUBLIC" in rendered:
                warn_hit = True
                break
        testbase.assert_equal(warn_hit, True)
    return


def test_connect_backward_compat_default_signature():
    """
        Existing call shape (host-only, no plane keyword) must continue
        to construct an SshBase identical to the pre-feature behaviour.
    """
    cred = _cred()
    ssh = DummySsh.connect(host="localhost", primary_credential=cred)
    testbase.assert_equal(isinstance(ssh, DummySsh), True)
    testbase.assert_equal(ssh.host, "localhost")
    return
