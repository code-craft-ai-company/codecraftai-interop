"""
Tests for :class:`TwingateClient` covering bring_up/bring_down/status,
self_address/peer_addresses asymmetry, dry-run, and aspect-driven elevation.
"""

import pathlib
from typing import List, Optional


from ccai.interfaces.icommandrunner import RunResult
from ccai.interfaces.ivpnclient import IVPNClient, VPNStatus

from ccai.interop.vpn.aspectsvpnclient import (
    AspectsVPNClient, DEFAULT_VPN_CLIENT_ASPECTS,
)
from ccai.interop.vpn.twingate.exceptions import (
    VPNBringDownError, VPNBringUpError,
)
from ccai.interop.vpn.twingate.twingateclient import TwingateClient
from ccai import testbase

from ccai.testbase.factories import create_log_capture


FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


class RecorderRunner:
    """A test double for :class:`ICommandRunner` that records every call."""

    def __init__(self, *, scripted_results: Optional[List[RunResult]] = None,
                 default_result: Optional[RunResult] = None):
        self.calls: List[dict] = []
        self._scripted = list(scripted_results) if scripted_results is not None else []
        self._default = default_result
        if self._default is None:
            self._default = RunResult(exit_code=0, stdout="", stderr="")
        return

    def run(self, args, *, elevated: bool = False, cwd=None, env=None,
            stdin=None, timeout=None, on_output=None, on_error=None,
            capture_output: bool = True) -> RunResult:
        self.calls.append({
            "args": list(args),
            "elevated": elevated,
            "timeout": timeout,
        })
        if len(self._scripted) > 0:
            result = self._scripted.pop(0)
        else:
            result = self._default
        return result


def _aspects(*, dry_run: bool = False, elevated: bool = False) -> AspectsVPNClient:
    aspects = AspectsVPNClient(dry_run=dry_run, elevated=elevated)
    return aspects


def test_twingateclient_conforms_to_ivpnclient_protocol():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    assert isinstance(client, IVPNClient)
    return


def test_bring_up_invokes_setup_then_start():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    status = client.bring_up(
        authkey="acc:ref", hostname="edge-01", aspects=_aspects()
    )
    assert len(runner.calls) == 2
    setup_argv = runner.calls[0]["args"]
    start_argv = runner.calls[1]["args"]
    assert setup_argv[0] == "twingate-connector"
    assert setup_argv[1] == "setup"
    assert "--access-token=acc" in setup_argv
    assert "--refresh-token=ref" in setup_argv
    assert "--name=edge-01" in setup_argv
    assert start_argv == ["systemctl", "start", "twingate-connector"]
    assert status.connected is True
    assert status.self_address is None
    assert status.backend_state == "Connected"
    assert status.hostname == "edge-01"
    return


def test_bring_up_includes_name_flag_when_hostname_supplied():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_up(authkey="a:b", hostname="my-host", aspects=_aspects())
    assert "--name=my-host" in runner.calls[0]["args"]
    return


def test_bring_up_omits_name_flag_when_hostname_absent():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_up(authkey="a:b", aspects=_aspects())
    flagged = [a for a in runner.calls[0]["args"] if a.startswith("--name")]
    assert flagged == []
    return


def test_bring_up_setup_failure_raises_VPNBringUpError():
    failure_text = (FIXTURES_DIR / "connector_setup_failure.txt").read_text()
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=1, stdout="", stderr=failure_text),
    ])
    client = TwingateClient(command_runner=runner)
    with testbase.raises(VPNBringUpError) as exc_info:
        client.bring_up(authkey="a:b", aspects=_aspects())
    assert exc_info.value.exit_code == 1
    assert "signature mismatch" in exc_info.value.stderr
    assert len(runner.calls) == 1
    return


def test_bring_up_start_failure_raises_VPNBringUpError():
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=0, stdout="", stderr=""),
        RunResult(exit_code=3, stdout="", stderr="unit not found"),
    ])
    client = TwingateClient(command_runner=runner)
    with testbase.raises(VPNBringUpError) as exc_info:
        client.bring_up(authkey="a:b", aspects=_aspects())
    assert exc_info.value.exit_code == 3
    assert "unit not found" in exc_info.value.stderr
    return


def test_bring_up_setup_failure_does_not_leak_tokens_in_error():
    # Regression for audit C8: the setup failure error message embeds the
    # setup argv, which carries --access-token / --refresh-token. Those token
    # values MUST be redacted before composing the VPNBringUpError message.
    access_token = "SUPERSECRETACCESS"
    refresh_token = "SUPERSECRETREFRESH"
    authkey = "{}:{}".format(access_token, refresh_token)
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=1, stdout="", stderr="setup rejected"),
    ])
    client = TwingateClient(command_runner=runner)
    with testbase.raises(VPNBringUpError) as exc_info:
        client.bring_up(authkey=authkey, aspects=_aspects())
    message = str(exc_info.value)
    assert access_token not in message
    assert refresh_token not in message
    assert "--access-token=***" in message
    assert "--refresh-token=***" in message
    return


def test_sanitize_argv_redacts_token_flag_values():
    from ccai.interop.vpn.twingate.twingateclient import sanitize_argv
    argv = [
        "twingate-connector", "setup",
        "--access-token=abc123", "--refresh-token=def456",
        "--name=edge-01",
    ]
    sanitized = sanitize_argv(argv)
    assert sanitized == [
        "twingate-connector", "setup",
        "--access-token=***", "--refresh-token=***",
        "--name=edge-01",
    ]
    return


def test_bring_up_dry_run_does_not_invoke_runner():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    status = client.bring_up(
        authkey="a:b", hostname="h", aspects=_aspects(dry_run=True)
    )
    assert runner.calls == []
    assert status.connected is False
    assert status.backend_state == "dry-run"
    assert status.self_address is None
    return


def test_bring_up_idempotent_repeat_calls_invoke_runner_twice_each():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_up(authkey="a:b", aspects=_aspects())
    client.bring_up(authkey="a:b", aspects=_aspects())
    assert len(runner.calls) == 4
    return


def test_bring_up_empty_authkey_raises_value_error():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    with testbase.raises(ValueError):
        client.bring_up(authkey="", aspects=_aspects())
    assert runner.calls == []
    return


def test_bring_down_invokes_systemctl_stop():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_down(aspects=_aspects())
    assert runner.calls[0]["args"] == ["systemctl", "stop", "twingate-connector"]
    return


def test_bring_down_non_zero_raises_VPNBringDownError():
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=5, stdout="", stderr="permission denied"),
    ])
    client = TwingateClient(command_runner=runner)
    with testbase.raises(VPNBringDownError) as exc_info:
        client.bring_down(aspects=_aspects())
    assert exc_info.value.exit_code == 5
    return


def test_bring_down_dry_run_skips_runner():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_down(aspects=_aspects(dry_run=True))
    assert runner.calls == []
    return


def test_status_maps_active_to_running_true():
    active_text = (FIXTURES_DIR / "systemctl_is_active.txt").read_text()
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=0, stdout=active_text, stderr=""),
    ])
    client = TwingateClient(command_runner=runner)
    status = client.status(aspects=_aspects())
    assert status.connected is True
    assert status.backend_state == "active"
    assert status.self_address is None
    return


def test_status_maps_inactive_to_running_false():
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=3, stdout="inactive\n", stderr=""),
    ])
    client = TwingateClient(command_runner=runner)
    status = client.status(aspects=_aspects())
    assert status.connected is False
    assert status.backend_state == "inactive"
    return


def test_status_maps_failed_without_raising():
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=3, stdout="failed\n", stderr=""),
    ])
    client = TwingateClient(command_runner=runner)
    status = client.status(aspects=_aspects())
    assert status.connected is False
    assert status.backend_state == "failed"
    return


def test_self_address_is_none_always():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    assert client.self_address() is None
    client.bring_up(authkey="a:b", aspects=_aspects(dry_run=True))
    assert client.self_address() is None
    return


@testbase.attach.parameter(create_log_capture, identifier="caplog")
def test_peer_addresses_is_empty_and_debug_logged_once(caplog):
    # Reset the process-once flag so this test owns the assertion.
    import ccai.interop.vpn.twingate.twingateclient as twcmod
    twcmod._PEER_ENUMERATION_WARNING_EMITTED = False

    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)

    import logging
    caplog.set_level(logging.DEBUG, logger=twcmod.__name__)

    first = client.peer_addresses()
    second = client.peer_addresses()
    third = client.peer_addresses()
    assert first == {}
    assert second == {}
    assert third == {}
    matching = [
        rec for rec in caplog.records
        if rec.name == twcmod.__name__ and "peer_addresses" in rec.getMessage()
    ]
    assert len(matching) == 1
    return


def test_writes_elevate_when_aspect_set():
    runner = RecorderRunner()
    client = TwingateClient(command_runner=runner)
    client.bring_up(authkey="a:b", aspects=_aspects(elevated=True))
    for call in runner.calls:
        assert call["elevated"] is True
    return


def test_reads_never_elevate():
    runner = RecorderRunner(scripted_results=[
        RunResult(exit_code=0, stdout="active", stderr=""),
    ])
    client = TwingateClient(command_runner=runner)
    client.status(aspects=_aspects(elevated=True))
    assert runner.calls[0]["elevated"] is False
    return
