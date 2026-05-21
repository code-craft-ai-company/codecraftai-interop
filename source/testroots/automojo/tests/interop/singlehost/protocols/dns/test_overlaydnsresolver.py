"""
    Unit and property tests for :class:`OverlayDNSResolver`.

    These tests cover the example-based acceptance criteria from
    ``specs/overlay-dns-resolver/requirements.md`` plus the mandatory
    ``hypothesis`` property tests for the overlay DNS feature (⊙).
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from hypothesis import HealthCheck, given, settings, strategies as st

from automojo.errors.exceptions import SemanticError

from automojo.interfaces.addressplane import AddressPlane
from automojo.interfaces.ivpnclient import IVPNClient
from automojo.interfaces.ivpncontrolplane import IVPNControlPlane, VPNDeviceRecord

from automojo.interop.protocols.dns.aspectsoverlaydns import (
    AspectsOverlayDNS,
    DEFAULT_OVERLAY_DNS_ASPECTS,
)
from automojo.interop.protocols.dns.exceptions import (
    OverlayDNSError,
    OverlayDNSNoMatchError,
)
from automojo.interop.protocols.dns.matchpredicate import is_match
from automojo.interop.protocols.dns.overlaycandidate import OverlayCandidate
from automojo.interop.protocols.dns.overlaydnsresolver import (
    KNOWN_OVERLAY_SUFFIXES,
    OverlayDNSResolver,
    OverlayDNSResolverRegistry,
)


def _make_vpn_client(*, peers: Dict[str, str]) -> IVPNClient:
    """
        Build a mock :class:`IVPNClient` returning the given peers.

        :param peers: Mapping of peer hostname to overlay IP.

        :returns: A configured :class:`MagicMock` typed as
            :class:`IVPNClient`.
    """
    client = MagicMock(spec=IVPNClient)
    client.peer_addresses.return_value = dict(peers)
    return client


def _make_control_plane(*, devices: List[VPNDeviceRecord]) -> IVPNControlPlane:
    """
        Build a mock :class:`IVPNControlPlane` returning the given
        devices.

        :param devices: List of device records.

        :returns: A configured :class:`MagicMock` typed as
            :class:`IVPNControlPlane`.
    """
    cp = MagicMock(spec=IVPNControlPlane)
    cp.list_devices.return_value = list(devices)
    return cp


# ---------------------------------------------------------------------------
# Example-based tests
# ---------------------------------------------------------------------------


def test_is_match_returns_true_for_overlay_suffix() -> None:
    """``is_match`` reports True for a name ending in a known suffix."""

    resolver = OverlayDNSResolver(
        vpn_clients=[_make_vpn_client(peers={})],
    )
    actual = resolver.is_match(name="myhost.tailnet.ts.net")
    assert actual is True
    return


def test_is_match_returns_false_for_normal_name() -> None:
    """``is_match`` reports False for a name that lacks any overlay suffix."""

    resolver = OverlayDNSResolver(
        vpn_clients=[_make_vpn_client(peers={})],
    )
    actual = resolver.is_match(name="example.com")
    assert actual is False
    return


def test_resolve_returns_overlay_address_for_matching_name() -> None:
    """``resolve`` returns the overlay address when a client matches."""

    client = _make_vpn_client(peers={"myhost": "100.64.0.1"})
    resolver = OverlayDNSResolver(vpn_clients=[client])
    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    actual = resolver.resolve(name="myhost", aspects=aspects)
    assert actual == "100.64.0.1"
    return


def test_resolve_returns_via_control_plane_when_no_client_match() -> None:
    """``resolve`` falls to control planes after client misses."""

    client = _make_vpn_client(peers={"other": "100.64.0.99"})
    record = VPNDeviceRecord(
        device_id="d1",
        hostname="myhost.tailnet.ts.net",
        overlay_address="100.64.0.7",
    )
    cp = _make_control_plane(devices=[record])
    resolver = OverlayDNSResolver(vpn_clients=[client], control_planes=[cp])
    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    actual = resolver.resolve(name="myhost", aspects=aspects)
    assert actual == "100.64.0.7"
    return


def test_resolve_raises_no_match_when_fall_through_disabled() -> None:
    """A miss with fall-through disabled raises ``OverlayDNSNoMatchError``."""

    client = _make_vpn_client(peers={"other": "100.64.0.99"})
    resolver = OverlayDNSResolver(vpn_clients=[client])
    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    with pytest.raises(OverlayDNSNoMatchError):
        resolver.resolve(name="missing", aspects=aspects)
    return


def test_resolve_falls_through_to_stdlib_when_enabled() -> None:
    """Stdlib resolver is consulted when fall-through is enabled."""

    client = _make_vpn_client(peers={})
    stub_calls = []

    def fake_stdlib(name: str) -> Optional[str]:
        stub_calls.append(name)
        return "203.0.113.10"

    resolver = OverlayDNSResolver(
        vpn_clients=[client],
        stdlib_resolver=fake_stdlib,
    )
    aspects = AspectsOverlayDNS(fall_through_standard_dns=True)
    actual = resolver.resolve(name="missing", aspects=aspects)
    assert actual == "203.0.113.10"
    assert stub_calls == ["missing"]
    return


def test_resolve_empty_peer_addresses_falls_through_or_misses() -> None:
    """An empty ``peer_addresses`` result must not match anything."""

    client = _make_vpn_client(peers={})
    resolver = OverlayDNSResolver(vpn_clients=[client])
    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    with pytest.raises(OverlayDNSNoMatchError):
        resolver.resolve(name="myhost", aspects=aspects)
    return


def test_resolve_overlay_with_no_providers_raises_semantic_error() -> None:
    """OVERLAY plane on an unconfigured resolver raises ``SemanticError``."""

    resolver = OverlayDNSResolver()
    with pytest.raises(SemanticError):
        resolver.resolve(name="anyhost")
    return


def test_resolve_public_plane_skips_overlay_path() -> None:
    """``PUBLIC`` plane goes straight to stdlib, no providers consulted."""

    client = _make_vpn_client(peers={"myhost": "100.64.0.1"})
    stub_calls = []

    def fake_stdlib(name: str) -> Optional[str]:
        stub_calls.append(name)
        return "203.0.113.5"

    resolver = OverlayDNSResolver(
        vpn_clients=[client],
        stdlib_resolver=fake_stdlib,
    )
    actual = resolver.resolve(name="myhost", plane=AddressPlane.PUBLIC)
    assert actual == "203.0.113.5"
    assert stub_calls == ["myhost"]
    client.peer_addresses.assert_not_called()
    return


def test_resolve_first_registered_provider_wins() -> None:
    """Earliest-registered provider returning a match wins."""

    first = _make_vpn_client(peers={"myhost": "100.64.0.1"})
    second = _make_vpn_client(peers={"myhost": "100.64.0.2"})
    resolver = OverlayDNSResolver(vpn_clients=[first, second])
    actual = resolver.resolve(
        name="myhost",
        aspects=AspectsOverlayDNS(fall_through_standard_dns=False),
    )
    assert actual == "100.64.0.1"
    second.peer_addresses.assert_not_called()
    return


def test_cache_hit_skips_providers() -> None:
    """Within TTL a second call must not re-consult the providers."""

    client = _make_vpn_client(peers={"myhost": "100.64.0.1"})
    resolver = OverlayDNSResolver(vpn_clients=[client])
    aspects = AspectsOverlayDNS(
        fall_through_standard_dns=False,
        cache_ttl_seconds=60.0,
    )

    first_result = resolver.resolve(name="myhost", aspects=aspects)
    second_result = resolver.resolve(name="myhost", aspects=aspects)

    assert first_result == "100.64.0.1"
    assert second_result == "100.64.0.1"
    assert client.peer_addresses.call_count == 1
    return


def test_register_vpn_client_appends_to_chain() -> None:
    """``register_vpn_client`` appends to the lookup chain."""

    resolver = OverlayDNSResolver()
    client = _make_vpn_client(peers={"myhost": "100.64.0.1"})
    resolver.register_vpn_client(client=client)
    actual = resolver.resolve(
        name="myhost",
        aspects=AspectsOverlayDNS(fall_through_standard_dns=False),
    )
    assert actual == "100.64.0.1"
    return


def test_registry_chains_multiple_resolvers_short_circuit() -> None:
    """Registry consults claiming resolvers in order and short-circuits."""

    ts_client = _make_vpn_client(peers={"myhost.ts.net": "100.64.0.1"})
    ts_resolver = OverlayDNSResolver(
        vpn_clients=[ts_client],
        known_suffixes=(".ts.net",),
    )

    tg_client = _make_vpn_client(peers={"myhost.ts.net": "100.99.99.99"})
    tg_resolver = OverlayDNSResolver(
        vpn_clients=[tg_client],
        known_suffixes=(".twingate.com",),
    )

    stub_calls = []

    def fake_stdlib(name: str) -> Optional[str]:
        stub_calls.append(name)
        return "203.0.113.5"

    registry = OverlayDNSResolverRegistry(
        resolvers=[ts_resolver, tg_resolver],
        stdlib_resolver=fake_stdlib,
    )

    # Tailscale claim short-circuits before Twingate.
    actual = registry.resolve(name="myhost.ts.net")
    assert actual == "100.64.0.1"
    tg_client.peer_addresses.assert_not_called()
    assert stub_calls == []

    # No suffix claim — falls through to stdlib.
    fallthrough = registry.resolve(name="example.com")
    assert fallthrough == "203.0.113.5"
    return


def test_control_plane_exception_is_wrapped() -> None:
    """An exception from a control plane is re-classified as ``OverlayDNSError``."""

    cp = MagicMock(spec=IVPNControlPlane)
    cp.list_devices.side_effect = RuntimeError("api blew up")

    resolver = OverlayDNSResolver(control_planes=[cp])
    with pytest.raises(OverlayDNSError):
        resolver.resolve(
            name="myhost",
            aspects=AspectsOverlayDNS(fall_through_standard_dns=False),
        )
    return


def test_client_semantic_error_is_not_swallowed() -> None:
    """
        Regression for audit IL-H2: a ``SemanticError`` raised by an
        ``IVPNClient.peer_addresses()`` call must bubble out unchanged rather
        than being re-classified as ``OverlayDNSError``.
    """
    client = MagicMock(spec=IVPNClient)
    client.peer_addresses.side_effect = SemanticError("misused api")

    resolver = OverlayDNSResolver(vpn_clients=[client])
    with pytest.raises(SemanticError):
        resolver.resolve(
            name="myhost",
            aspects=AspectsOverlayDNS(fall_through_standard_dns=False),
        )
    return


def test_control_plane_semantic_error_is_not_swallowed() -> None:
    """
        Regression for audit IL-H3: a ``SemanticError`` raised by an
        ``IVPNControlPlane.list_devices()`` call must bubble out unchanged
        rather than being re-classified as ``OverlayDNSError``.
    """
    cp = MagicMock(spec=IVPNControlPlane)
    cp.list_devices.side_effect = SemanticError("misused api")

    resolver = OverlayDNSResolver(control_planes=[cp])
    with pytest.raises(SemanticError):
        resolver.resolve(
            name="myhost",
            aspects=AspectsOverlayDNS(fall_through_standard_dns=False),
        )
    return


# ---------------------------------------------------------------------------
# Property tests (hypothesis) — required for this feature
# ---------------------------------------------------------------------------


_candidate_strategy = st.builds(
    OverlayCandidate,
    short_hostname=st.text(min_size=0, max_size=40),
    magicdns_name=st.one_of(st.none(), st.text(min_size=0, max_size=60)),
    addresses=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=3),
    provider=st.text(min_size=0, max_size=20),
)


@given(query=st.text(), candidate=_candidate_strategy)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_is_match_predicate_is_total(query, candidate) -> None:
    """For any ``(str, OverlayCandidate)`` pair, ``is_match`` returns a bool."""

    result = is_match(query=query, candidate=candidate)
    assert isinstance(result, bool)
    return


@given(query=st.text(), candidate=_candidate_strategy)
def test_is_match_predicate_is_deterministic(query, candidate) -> None:
    """``is_match`` is deterministic — same input, same output."""

    first = is_match(query=query, candidate=candidate)
    second = is_match(query=query, candidate=candidate)
    assert first == second
    return


@given(name=st.text())
def test_resolver_is_match_is_total(name) -> None:
    """``OverlayDNSResolver.is_match`` returns a bool for any string."""

    resolver = OverlayDNSResolver(vpn_clients=[_make_vpn_client(peers={})])
    result = resolver.is_match(name=name)
    assert isinstance(result, bool)
    return


@given(name=st.text())
def test_resolver_is_match_is_deterministic(name) -> None:
    """``OverlayDNSResolver.is_match`` is deterministic across calls."""

    resolver = OverlayDNSResolver(vpn_clients=[_make_vpn_client(peers={})])
    first = resolver.is_match(name=name)
    second = resolver.is_match(name=name)
    assert first == second
    return


_hostname_strategy = st.text(
    alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
    min_size=1,
    max_size=12,
)
_ip_strategy = st.builds(
    lambda a, b, c, d: "{}.{}.{}.{}".format(a, b, c, d),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
)


@given(
    base_peers=st.dictionaries(
        keys=_hostname_strategy, values=_ip_strategy, min_size=1, max_size=5
    ),
    extra_peers=st.dictionaries(
        keys=_hostname_strategy, values=_ip_strategy, min_size=0, max_size=5
    ),
)
def test_resolve_is_monotonic_in_peers(base_peers, extra_peers) -> None:
    """Adding peers cannot make a previously-resolved name unresolvable."""

    # Pick a target name that exists in ``base_peers``.
    target_name = sorted(base_peers.keys())[0]
    expected_address = base_peers[target_name]

    base_client = _make_vpn_client(peers=base_peers)
    base_resolver = OverlayDNSResolver(vpn_clients=[base_client])
    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    base_answer = base_resolver.resolve(name=target_name, aspects=aspects)
    assert base_answer == expected_address

    merged = dict(base_peers)
    # ``extra_peers`` must not overwrite the target's entry — preserve it.
    for key, value in extra_peers.items():
        if key != target_name:
            merged[key] = value

    grown_client = _make_vpn_client(peers=merged)
    grown_resolver = OverlayDNSResolver(vpn_clients=[grown_client])
    grown_answer = grown_resolver.resolve(name=target_name, aspects=aspects)
    assert grown_answer == expected_address
    return


@given(name=st.text(min_size=1, max_size=30))
def test_resolver_outcome_consistent_with_is_match(name) -> None:
    """If ``is_match(name)`` is True the resolver may produce a match;
    otherwise the resolver misses overlay state (because no peer can
    structurally match an unknown-suffix name in this fixture)."""

    resolver = OverlayDNSResolver(
        vpn_clients=[_make_vpn_client(peers={})],
    )
    claimed = resolver.is_match(name=name)
    assert isinstance(claimed, bool)

    aspects = AspectsOverlayDNS(fall_through_standard_dns=False)
    # With no peers the overlay path always misses regardless of suffix —
    # the resolver therefore raises NoMatch. This verifies the resolver
    # never silently returns ``None`` on overlay misses.
    with pytest.raises(OverlayDNSNoMatchError):
        resolver.resolve(name=name, aspects=aspects)
    return
