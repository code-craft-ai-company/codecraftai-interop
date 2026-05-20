"""
    .. module:: overlaydnsresolver
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`OverlayDNSResolver` and
                   the :class:`OverlayDNSResolverRegistry` helper.

    :class:`OverlayDNSResolver` maps short / MagicDNS / Twingate-resource
    names to overlay addresses by walking a registered list of
    :class:`IVPNClient` and :class:`IVPNControlPlane` providers and falling
    through to the standard system DNS resolver when no overlay match is
    found.

    The matching predicate (see :mod:`matchpredicate`) is a pure, total,
    deterministic function. This resolver is the I/O-bound shell wrapping
    that predicate; behaviour-modifying decorators are not used — the
    caller controls behaviour through an :class:`AspectsOverlayDNS`
    instance passed on every call.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os
import socket
import time

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from automojo.aspects.aspects import Aspects
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


# Known overlay-DNS suffixes used by the cheap, syntactic ``is_match``
# instance method. The deeper match against provider state happens inside
# :meth:`OverlayDNSResolver.resolve`; this list is only used to answer the
# question "is the syntactic shape of this name plausibly an overlay name?".
KNOWN_OVERLAY_SUFFIXES: Tuple[str, ...] = (
    ".ts.net",          # Tailscale MagicDNS
    ".tailnet.ts.net",  # Tailscale MagicDNS (alias)
    ".twingate.com",    # Twingate-managed FQDNs
)


@dataclass
class _CacheEntry:
    """
        Internal cache entry for resolved overlay addresses.

        :param address: The cached resolved address.
        :param expires_at: Monotonic deadline after which the entry must
            be re-queried.
    """
    address: str
    expires_at: float


class OverlayDNSResolver:
    """
        Resolver mapping overlay names to overlay addresses via registered
        VPN clients and control planes, with optional fall-through to the
        standard system resolver.
    """

    def __init__(
        self,
        *,
        vpn_clients: Optional[List[IVPNClient]] = None,
        control_planes: Optional[List[IVPNControlPlane]] = None,
        stdlib_resolver: Optional[Callable[[str], Optional[str]]] = None,
        default_aspects: AspectsOverlayDNS = DEFAULT_OVERLAY_DNS_ASPECTS,
        known_suffixes: Optional[Tuple[str, ...]] = None,
        provider_aspects: Optional[Aspects] = None,
    ) -> None:
        """
            Construct a new overlay DNS resolver.

            :param vpn_clients: Initial list of :class:`IVPNClient`
                instances to consult, in registration order. ``None`` is
                treated as an empty list.
            :param control_planes: Initial list of
                :class:`IVPNControlPlane` instances to consult after the
                clients, in registration order. ``None`` is treated as an
                empty list.
            :param stdlib_resolver: Optional injectable standard resolver
                used for fall-through and for ``PUBLIC`` / ``PRIVATE``
                planes. When ``None``, :func:`socket.gethostbyname` is
                used.
            :param default_aspects: Default :class:`AspectsOverlayDNS`
                applied to calls that do not pass aspects explicitly.
            :param known_suffixes: Known overlay-name suffixes used by the
                syntactic :meth:`is_match` instance method. When ``None``
                the module-level :data:`KNOWN_OVERLAY_SUFFIXES` tuple is
                used.
            :param provider_aspects: :class:`Aspects` to forward to
                :meth:`IVPNControlPlane.list_devices`. When ``None`` a
                fresh default :class:`Aspects` is constructed at call
                time.
        """

        if vpn_clients is None:
            self._vpn_clients: List[IVPNClient] = []
        else:
            self._vpn_clients = list(vpn_clients)

        if control_planes is None:
            self._control_planes: List[IVPNControlPlane] = []
        else:
            self._control_planes = list(control_planes)

        if stdlib_resolver is None:
            self._stdlib_resolver = _default_stdlib_resolver
        else:
            self._stdlib_resolver = stdlib_resolver

        self._default_aspects: AspectsOverlayDNS = default_aspects

        if known_suffixes is None:
            self._known_suffixes: Tuple[str, ...] = KNOWN_OVERLAY_SUFFIXES
        else:
            self._known_suffixes = tuple(known_suffixes)

        self._provider_aspects: Optional[Aspects] = provider_aspects

        self._cache: Dict[Tuple[str, AddressPlane], _CacheEntry] = {}

        return

    def register_vpn_client(self, *, client: IVPNClient) -> None:
        """
            Append a VPN client to the resolver's lookup chain.

            :param client: The :class:`IVPNClient` to register.

            :returns: ``None``.
        """
        self._vpn_clients.append(client)
        return

    def register_control_plane(self, *, cp: IVPNControlPlane) -> None:
        """
            Append a VPN control plane to the resolver's lookup chain.

            :param cp: The :class:`IVPNControlPlane` to register.

            :returns: ``None``.
        """
        self._control_planes.append(cp)
        return

    def is_match(self, *, name: str) -> bool:
        """
            Pure, total, deterministic predicate reporting whether
            ``name`` is syntactically a plausible overlay name.

            The predicate is a cheap structural check used by callers
            (and by the registry) to decide whether to invoke
            :meth:`resolve` at all. It does NOT consult provider state
            and never raises.

            :param name: The candidate name to test.

            :returns: ``True`` when ``name`` ends with one of the
                resolver's known overlay suffixes (case-insensitively),
                otherwise ``False``. Non-string and empty inputs return
                ``False``.
        """

        if not isinstance(name, str):
            rtnval = False
            return rtnval

        if len(name) == 0:
            rtnval = False
            return rtnval

        lower_name = name.lower()

        rtnval = False
        for suffix in self._known_suffixes:
            suffix_lower = suffix.lower()
            if lower_name.endswith(suffix_lower):
                rtnval = True
                break

        return rtnval

    def resolve(
        self,
        *,
        name: str,
        plane: AddressPlane = AddressPlane.OVERLAY,
        aspects: Optional[AspectsOverlayDNS] = None,
    ) -> Optional[str]:
        """
            Resolve ``name`` on the requested plane.

            On ``OVERLAY`` the resolver consults each registered VPN
            client (in registration order) and then each registered
            control plane (in registration order), returning the first
            match. On miss the resolver either falls through to the
            standard system resolver (when
            ``aspects.fall_through_standard_dns`` is ``True``) or raises
            :class:`OverlayDNSNoMatchError`.

            On ``PUBLIC`` / ``PRIVATE`` the resolver bypasses the overlay
            path and invokes the standard resolver directly.

            :param name: The name to resolve.
            :param plane: The :class:`AddressPlane` to resolve on.
            :param aspects: Behaviour control. When ``None`` the
                resolver's ``default_aspects`` is used.

            :returns: The resolved address, or ``None`` when the
                resolver could not produce an address and fall-through
                yielded no answer either (only possible when the standard
                resolver itself returns ``None``).

            :raises SemanticError: When ``plane=OVERLAY`` is requested
                and no providers are registered.
            :raises OverlayDNSNoMatchError: When no provider matches and
                fall-through is disabled.
        """

        if aspects is None:
            aspects = self._default_aspects

        if plane != AddressPlane.OVERLAY:
            rtnval = self._stdlib_resolver(name)
            return rtnval

        n_clients = len(self._vpn_clients)
        n_planes = len(self._control_planes)
        if n_clients == 0 and n_planes == 0:
            err_msg_lines = [
                "OverlayDNSResolver.resolve was called with plane=OVERLAY but",
                "no IVPNClient or IVPNControlPlane providers are registered.",
                "Register at least one provider before requesting OVERLAY resolution.",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg)

        cache_key = (name, plane)

        if aspects.cache_ttl_seconds > 0.0:
            cached = self._cache.get(cache_key)
            now = time.monotonic()
            if cached is not None and cached.expires_at > now:
                rtnval = cached.address
                return rtnval

        matched_address = self._lookup_via_clients(name=name, aspects=aspects)

        if matched_address is None:
            matched_address = self._lookup_via_control_planes(
                name=name, aspects=aspects
            )

        if matched_address is not None:
            if aspects.cache_ttl_seconds > 0.0:
                now = time.monotonic()
                entry = _CacheEntry(
                    address=matched_address,
                    expires_at=now + aspects.cache_ttl_seconds,
                )
                self._cache[cache_key] = entry
            rtnval = matched_address
            return rtnval

        if aspects.fall_through_standard_dns:
            rtnval = self._stdlib_resolver(name)
            return rtnval

        err_msg_lines = [
            "OverlayDNSResolver: no overlay provider produced a match for the name.",
            "QUERY: {}".format(name),
            "PROVIDERS CONSULTED:",
            "    IVPNClient instances: {}".format(n_clients),
            "    IVPNControlPlane instances: {}".format(n_planes),
            "FALL-THROUGH DISABLED: aspects.fall_through_standard_dns is False.",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise OverlayDNSNoMatchError(err_msg)

    def _lookup_via_clients(
        self,
        *,
        name: str,
        aspects: AspectsOverlayDNS,
    ) -> Optional[str]:
        """
            Walk the registered VPN clients in order and return the first
            matching overlay address, or ``None`` when no client matches.

            :param name: The query name.
            :param aspects: Behaviour control forwarded to the matching
                predicate.

            :returns: The matching overlay address, or ``None``.

            :raises OverlayDNSError: When a client's enumeration call
                raises unexpectedly.
        """

        rtnval: Optional[str] = None

        for client in self._vpn_clients:
            try:
                peers = client.peer_addresses()
            except Exception as xcpt:
                err_msg_lines = [
                    "OverlayDNSResolver: IVPNClient.peer_addresses() raised.",
                    "CLIENT: {}".format(client),
                ]
                err_msg = os.linesep.join(err_msg_lines)
                raise OverlayDNSError(err_msg) from xcpt

            if peers is None:
                continue

            if len(peers) == 0:
                continue

            for host, addr in peers.items():
                if addr is None:
                    continue
                candidate = OverlayCandidate(
                    short_hostname=host,
                    magicdns_name=None,
                    addresses=[addr],
                    provider="",
                )
                matched = is_match(
                    query=name,
                    candidate=candidate,
                    aspects=aspects,
                )
                if matched:
                    rtnval = addr
                    return rtnval

        return rtnval

    def _lookup_via_control_planes(
        self,
        *,
        name: str,
        aspects: AspectsOverlayDNS,
    ) -> Optional[str]:
        """
            Walk the registered control planes in order and return the
            first matching overlay address, or ``None`` when no control
            plane matches.

            :param name: The query name.
            :param aspects: Behaviour control forwarded to the matching
                predicate.

            :returns: The matching overlay address, or ``None``.

            :raises OverlayDNSError: When a control plane's enumeration
                call raises unexpectedly.
        """

        rtnval: Optional[str] = None

        provider_aspects = self._provider_aspects
        if provider_aspects is None:
            provider_aspects = Aspects()

        for cp in self._control_planes:
            try:
                devices = cp.list_devices(aspects=provider_aspects)
            except Exception as xcpt:
                err_msg_lines = [
                    "OverlayDNSResolver: IVPNControlPlane.list_devices() raised.",
                    "CONTROL_PLANE: {}".format(cp),
                ]
                err_msg = os.linesep.join(err_msg_lines)
                raise OverlayDNSError(err_msg) from xcpt

            if devices is None:
                continue

            for device in devices:
                candidate = _candidate_from_device(device=device)
                if candidate is None:
                    continue
                matched = is_match(
                    query=name,
                    candidate=candidate,
                    aspects=aspects,
                )
                if matched:
                    addr = candidate.addresses[0] if len(candidate.addresses) > 0 else None
                    if addr is not None:
                        rtnval = addr
                        return rtnval

        return rtnval


class OverlayDNSResolverRegistry:
    """
        Chain helper that owns multiple overlay resolvers (e.g. one for
        Tailscale and one for Twingate) and falls through to standard DNS
        when none of them match.
    """

    def __init__(
        self,
        *,
        resolvers: Optional[List[OverlayDNSResolver]] = None,
        stdlib_resolver: Optional[Callable[[str], Optional[str]]] = None,
        default_aspects: AspectsOverlayDNS = DEFAULT_OVERLAY_DNS_ASPECTS,
    ) -> None:
        """
            Construct a new chained overlay resolver registry.

            :param resolvers: Initial list of :class:`OverlayDNSResolver`
                instances in priority order. ``None`` is treated as
                empty.
            :param stdlib_resolver: Optional injectable standard resolver
                used for the final fall-through.
            :param default_aspects: Default aspects forwarded to child
                resolvers when the caller does not pass aspects.
        """

        if resolvers is None:
            self._resolvers: List[OverlayDNSResolver] = []
        else:
            self._resolvers = list(resolvers)

        if stdlib_resolver is None:
            self._stdlib_resolver = _default_stdlib_resolver
        else:
            self._stdlib_resolver = stdlib_resolver

        self._default_aspects: AspectsOverlayDNS = default_aspects

        return

    def register(self, *, resolver: OverlayDNSResolver) -> None:
        """
            Append an overlay resolver to the chain.

            :param resolver: The resolver to register.

            :returns: ``None``.
        """
        self._resolvers.append(resolver)
        return

    def resolve(
        self,
        *,
        name: str,
        aspects: Optional[AspectsOverlayDNS] = None,
    ) -> Optional[str]:
        """
            Resolve ``name`` by walking the registered resolvers in
            order. The first resolver whose :meth:`is_match` returns
            ``True`` is consulted; if it produces an address that
            address is returned. If no resolver claims the name (or all
            claimants miss) the registry falls through to the standard
            system resolver.

            :param name: The name to resolve.
            :param aspects: Behaviour control forwarded to the matching
                resolver. When ``None`` the registry's
                ``default_aspects`` is used.

            :returns: The resolved address, or ``None`` when both the
                overlay chain and the standard resolver miss.
        """

        if aspects is None:
            aspects = self._default_aspects

        # Short-circuit at the first resolver that claims the name.
        for resolver in self._resolvers:
            claimed = resolver.is_match(name=name)
            if claimed:
                # Build a per-call aspects that disables fall-through
                # because the registry owns fall-through.
                local_aspects = AspectsOverlayDNS(
                    fall_through_standard_dns=False,
                    query_timeout_seconds=aspects.query_timeout_seconds,
                    case_sensitive=aspects.case_sensitive,
                    cache_ttl_seconds=aspects.cache_ttl_seconds,
                )
                try:
                    matched_address = resolver.resolve(
                        name=name,
                        plane=AddressPlane.OVERLAY,
                        aspects=local_aspects,
                    )
                except OverlayDNSNoMatchError:
                    matched_address = None

                if matched_address is not None:
                    rtnval = matched_address
                    return rtnval

        rtnval = self._stdlib_resolver(name)
        return rtnval


def _candidate_from_device(*, device: VPNDeviceRecord) -> Optional[OverlayCandidate]:
    """
        Build an :class:`OverlayCandidate` from a
        :class:`VPNDeviceRecord`, splitting the device hostname into a
        short hostname and (when dotted) a MagicDNS-style FQDN.

        :param device: The device record returned by a control plane.

        :returns: An :class:`OverlayCandidate` populated from the record,
            or ``None`` when the record carries no overlay address.
    """

    if device is None:
        rtnval = None
        return rtnval

    overlay_address = device.overlay_address
    if overlay_address is None:
        rtnval = None
        return rtnval

    hostname = device.hostname
    if hostname is None:
        hostname = ""

    if "." in hostname:
        short_hostname = hostname.split(".", 1)[0]
        magicdns_name = hostname
    else:
        short_hostname = hostname
        magicdns_name = None

    rtnval = OverlayCandidate(
        short_hostname=short_hostname,
        magicdns_name=magicdns_name,
        addresses=[overlay_address],
        provider="",
    )
    return rtnval


def _default_stdlib_resolver(name: str) -> Optional[str]:
    """
        Default fall-through resolver delegating to
        :func:`socket.gethostbyname`.

        :param name: The name to resolve.

        :returns: The resolved address string, or ``None`` when the
            stdlib resolver cannot resolve the name.
    """

    rtnval: Optional[str] = None
    try:
        rtnval = socket.gethostbyname(name)
    except OSError:
        rtnval = None
    return rtnval


__all__ = [
    "OverlayDNSResolver",
    "OverlayDNSResolverRegistry",
    "KNOWN_OVERLAY_SUFFIXES",
]
