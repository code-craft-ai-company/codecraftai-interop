"""
Tests for the pure argv-composition helpers in
:mod:`ccai.interop.vpn.twingate.connectorinvocation`.
"""

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.interop.vpn.twingate.connectorinvocation import (
    compose_service_argv,
    compose_setup_argv,
)

from ccai import testbase


def test_compose_setup_argv_splits_token_bundle():
    argv = compose_setup_argv(authkey="access-AAA:refresh-BBB")
    assert argv == [
        "twingate-connector",
        "setup",
        "--access-token=access-AAA",
        "--refresh-token=refresh-BBB",
    ]
    return


def test_compose_setup_argv_includes_name_flag_when_hostname_supplied():
    argv = compose_setup_argv(
        authkey="access-AAA:refresh-BBB", hostname="edge-01"
    )
    assert argv[-1] == "--name=edge-01"
    return


def test_compose_setup_argv_omits_name_flag_when_hostname_absent():
    argv = compose_setup_argv(authkey="access-AAA:refresh-BBB")
    flags = [arg for arg in argv if arg.startswith("--name")]
    assert flags == []
    return


def test_compose_setup_argv_rejects_empty_authkey():
    with testbase.raises(ValueError):
        compose_setup_argv(authkey="")
    return


def test_compose_setup_argv_rejects_missing_colon():
    with testbase.raises(ValueError):
        compose_setup_argv(authkey="just-one-token")
    return


def test_compose_setup_argv_rejects_empty_half():
    with testbase.raises(ValueError):
        compose_setup_argv(authkey="access:")
    with testbase.raises(ValueError):
        compose_setup_argv(authkey=":refresh")
    return


def test_compose_service_argv_emits_systemctl_call():
    argv_start = compose_service_argv(action="start")
    argv_stop = compose_service_argv(action="stop")
    argv_status = compose_service_argv(action="is-active")
    assert argv_start == ["systemctl", "start", "twingate-connector"]
    assert argv_stop == ["systemctl", "stop", "twingate-connector"]
    assert argv_status == ["systemctl", "is-active", "twingate-connector"]
    return


@given(
    access=st.text(
        alphabet=st.characters(blacklist_characters=":\x00\n\r"),
        min_size=1,
        max_size=64,
    ),
    refresh=st.text(
        alphabet=st.characters(blacklist_characters=":\x00\n\r"),
        min_size=1,
        max_size=64,
    ),
    hostname=st.one_of(
        st.none(),
        st.text(
            alphabet=st.characters(
                whitelist_categories=("L", "N"),
                whitelist_characters="-.",
            ),
            min_size=1,
            max_size=32,
        ),
    ),
)
def test_setup_argv_body_shape_is_stable(access, refresh, hostname):
    authkey = f"{access}:{refresh}"
    argv = compose_setup_argv(authkey=authkey, hostname=hostname)
    assert argv[0] == "twingate-connector"
    assert argv[1] == "setup"
    assert argv[2] == f"--access-token={access}"
    assert argv[3] == f"--refresh-token={refresh}"
    if hostname is not None and len(hostname) > 0:
        assert argv[4] == f"--name={hostname}"
    return
