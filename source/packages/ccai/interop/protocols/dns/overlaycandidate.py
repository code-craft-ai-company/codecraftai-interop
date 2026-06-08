"""
    .. module:: overlaycandidate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`OverlayCandidate`
                   dataclass — the value-object on which the overlay DNS
                   matching predicate operates.

    An :class:`OverlayCandidate` is the normalised view of a peer record (as
    produced by :meth:`IVPNClient.peer_addresses`) or a device record (as
    produced by :meth:`IVPNControlPlane.list_devices`) that the matching
    predicate compares a query string against.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OverlayCandidate:
    """
        Normalised candidate record consulted by the overlay DNS matching
        predicate.

        :param short_hostname: The peer's short host name as advertised by
            the provider (e.g. ``"myhost"``).
        :param magicdns_name: The provider's fully-qualified MagicDNS name
            when one exists (e.g. ``"myhost.tailnet.ts.net"``). May be
            ``None`` for providers that do not assign FQDNs per peer.
        :param addresses: One or more overlay addresses associated with the
            candidate. The first entry is taken as the canonical address.
        :param provider: Provider identifier, for example ``"tailscale"``
            or ``"twingate"``.
    """
    short_hostname: str
    magicdns_name: Optional[str] = None
    addresses: List[str] = field(default_factory=list)
    provider: str = ""


__all__ = ["OverlayCandidate"]
