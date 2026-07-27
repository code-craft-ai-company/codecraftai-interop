"""
Tests for :class:`TailscaleClient` covering bring_up/down, status parsing,
peer enumeration, and aspect-driven elevation/dry-run.
"""

import json
import os
import pathlib
from typing import Dict, List, Optional

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.interfaces.icommandrunner import RunResult
from ccai.interfaces.ivpnclient import IVPNClient, VPNStatus

from ccai.interop.vpn.aspectsvpnclient import (
    AspectsVPNClient, DEFAULT_VPN_CLIENT_ASPECTS
)
from ccai.interop.vpn.tailscale.exceptions import (
    VPNBringDownError, VPNBringUpError, VPNStatusError
)
from ccai.interop.vpn.tailscale.tailscaleclient import TailscaleClient
from ccai import testbase


FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


class RecorderRunner:
    """Records each invocation and returns a configured RunResult."""

    def __init__(self):
        self.calls: List[Dict] = []
        self.next_result = RunResult(exit_code=0, stdout="", stderr="")

    def run(self, args, *, elevated: bool = False, cwd: Optional[str] = None,
            env: Optional[Dict] = None, stdin: Optional[str] = None,
            timeout: Optional[float] = None, on_output=None, on_error=None,
            capture_output: bool = True) -> RunResult:
        call_record = {
            "args": list(args),
            "elevated": elevated,
            "timeout": timeout,
        }
        self.calls.append(call_record)
        return self.next_result


def _load_fixture(name: str) -> str:
    path = FIXTURES_DIR / name
    rtnval = path.read_text(encoding="utf-8")
    return rtnval


def _ts_argv_match(call_args: List[str], expected_first: List[str]) -> bool:
    if len(call_args) < len(expected_first):
        return False
    return call_args[: len(expected_first)] == expected_first


def test_isinstance_ivpnclient():
    runner = RecorderRunner()
    client = TailscaleClient(command_runner=runner)
    assert isinstance(client, IVPNClient) is True
    return


def test_bring_up_composes_argv_with_all_flags():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)

    client.bring_up(authkey="tskey-AUTH", hostname="lab-01",
                    advertise_tags=["tag:lab", "tag:test"])

    up_call = runner.calls[0]
    assert up_call["args"] == [
        "tailscale", "up",
        "--authkey=tskey-AUTH",
        "--hostname=lab-01",
        "--advertise-tags=tag:lab,tag:test",
    ]
    return


def test_bring_up_omits_hostname_when_none():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    client.bring_up(authkey="tskey-AUTH", hostname=None, advertise_tags=["tag:lab"])
    up_args = runner.calls[0]["args"]
    assert "--hostname" not in " ".join(up_args)
    assert any(a.startswith("--advertise-tags=") for a in up_args)
    return


def test_bring_up_omits_tags_when_empty():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    client.bring_up(authkey="tskey-AUTH", hostname="h", advertise_tags=[])
    up_args = runner.calls[0]["args"]
    assert not any(a.startswith("--advertise-tags") for a in up_args)
    return


def test_bring_up_dry_run_does_not_invoke_runner():
    runner = RecorderRunner()
    client = TailscaleClient(command_runner=runner)
    aspects = AspectsVPNClient(dry_run=True)
    result = client.bring_up(authkey="tskey-AUTH", aspects=aspects)
    assert len(runner.calls) == 0
    assert result.connected is False
    assert result.backend_state == "dry-run"
    return


def test_bring_up_non_zero_raises_vpnbringuperror():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=1, stdout="", stderr="auth rejected")
    client = TailscaleClient(command_runner=runner)
    with testbase.raises(VPNBringUpError) as excinfo:
        client.bring_up(authkey="tskey-AUTH")
    assert excinfo.value.exit_code == 1
    assert "auth rejected" in excinfo.value.stderr
    return


def test_bring_down_invokes_tailscale_down():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout="", stderr="")
    client = TailscaleClient(command_runner=runner)
    client.bring_down()
    assert runner.calls[0]["args"] == ["tailscale", "down"]
    return


def test_bring_down_non_zero_raises():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=2, stdout="", stderr="not running")
    client = TailscaleClient(command_runner=runner)
    with testbase.raises(VPNBringDownError) as excinfo:
        client.bring_down()
    assert excinfo.value.exit_code == 2
    return


def test_bring_down_dry_run_skips_runner():
    runner = RecorderRunner()
    client = TailscaleClient(command_runner=runner)
    aspects = AspectsVPNClient(dry_run=True)
    client.bring_down(aspects=aspects)
    assert len(runner.calls) == 0
    return


def test_status_parses_running_fixture():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    result: VPNStatus = client.status()
    assert result.connected is True
    assert result.backend_state == "Running"
    assert result.self_address == "100.64.10.5"
    assert result.hostname == "lab-host-01"
    assert "tag:lab" in result.tags
    assert result.provider == "tailscale"
    return


def test_status_handles_logged_out_without_raising():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=1, stdout="",
                                   stderr="Logged out. Use tailscale up to log back in.")
    client = TailscaleClient(command_runner=runner)
    result = client.status()
    assert result.connected is False
    return


def test_status_corrupt_json_raises_vpnstatuserror():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout="{not-json", stderr="")
    client = TailscaleClient(command_runner=runner)
    with testbase.raises(VPNStatusError):
        client.status()
    return


def test_self_address_returns_cached_value():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    client.status()
    addr = client.self_address()
    assert addr == "100.64.10.5"
    # self_address with cached state should not invoke a second call
    assert len(runner.calls) == 1
    return


def test_self_address_refreshes_when_no_cache():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    addr = client.self_address()
    assert addr == "100.64.10.5"
    assert len(runner.calls) == 1
    return


def test_peer_addresses_picks_cgnat_address():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_with_peers.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    peers = client.peer_addresses()
    assert peers["peer-a"] == "100.64.20.7"
    assert peers["peer-b"] == "100.64.30.8"
    # peer-c has no addresses -> omitted
    assert "peer-c" not in peers
    return


def test_peer_addresses_empty_when_no_peers():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    peers = client.peer_addresses()
    assert peers == {}
    return


def test_writes_elevate_when_aspect_set():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    aspects = AspectsVPNClient(elevated=True)
    client.bring_up(authkey="tskey-X", aspects=aspects)
    up_call = runner.calls[0]
    assert up_call["elevated"] is True
    # The status follow-up should not elevate
    status_call = runner.calls[1]
    assert status_call["elevated"] is False
    return


def test_reads_never_elevate():
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    aspects = AspectsVPNClient(elevated=True)
    client.status(aspects=aspects)
    assert runner.calls[0]["elevated"] is False
    return


# ---------- property tests ----------

_TAG_STRAT = st.lists(st.sampled_from(["tag:lab", "tag:test", "tag:ci", "tag:prov"]),
                       min_size=0, max_size=4, unique=True)


@given(
    constraints={"max_examples": 25},authkey=st.text(min_size=1, max_size=24,
                       alphabet=st.characters(min_codepoint=33, max_codepoint=126,
                                              blacklist_characters=" \t\n\r")),
       hostname=st.one_of(st.none(), st.text(min_size=1, max_size=10,
                                             alphabet=st.characters(
                                                 whitelist_categories=("Ll", "Lu", "Nd")))),
       tags=_TAG_STRAT)
def test_bring_up_argv_is_deterministic(authkey, hostname, tags):
    runner_a = RecorderRunner()
    runner_a.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client_a = TailscaleClient(command_runner=runner_a)
    client_a.bring_up(authkey=authkey, hostname=hostname, advertise_tags=tags)

    runner_b = RecorderRunner()
    runner_b.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client_b = TailscaleClient(command_runner=runner_b)
    client_b.bring_up(authkey=authkey, hostname=hostname, advertise_tags=tags)

    assert runner_a.calls[0]["args"] == runner_b.calls[0]["args"]
    return


@given(call_count=st.integers(min_value=2, max_value=6), constraints={"max_examples": 15})
def test_bring_up_idempotent_sequence_converges(call_count):
    runner = RecorderRunner()
    runner.next_result = RunResult(exit_code=0, stdout=_load_fixture("status_running.json"), stderr="")
    client = TailscaleClient(command_runner=runner)
    last_result = None
    for _ in range(call_count):
        last_result = client.bring_up(authkey="tskey-K")
    assert last_result is not None
    assert last_result.connected is True
    return
