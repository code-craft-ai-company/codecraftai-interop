"""
    .. module:: aspectsoverlaydns
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AspectsOverlayDNS`
                   dataclass and the :data:`DEFAULT_OVERLAY_DNS_ASPECTS`
                   sentinel used by :class:`OverlayDNSResolver`.

    Aspects ride on every call to the overlay DNS resolver, packaging the
    behavioural knobs (fall-through, timeout, case-sensitivity, caching) into
    a single scalable parameter following the project's Aspects pattern.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass

from ccai.aspects.aspects import Aspects as AspectsBase


@dataclass(eq=False)
class AspectsOverlayDNS(AspectsBase):
    """
        Behaviour-control aspects for the overlay DNS resolver.

        :param fall_through_standard_dns: When ``True`` the resolver falls
            through to the standard system DNS resolver after every
            registered overlay provider misses. When ``False`` the resolver
            raises :class:`OverlayDNSNoMatchError` on a miss.
        :param query_timeout_seconds: Upper bound on the time spent
            consulting providers and the fall-through resolver for a single
            query.
        :param case_sensitive: When ``False`` (the default) both the query
            and the candidate name are folded to lowercase before matching.
        :param cache_ttl_seconds: Time-to-live for cached
            ``(name, plane) -> address`` entries. When ``0`` caching is
            disabled.
    """
    fall_through_standard_dns: bool = True
    query_timeout_seconds: float = 5.0
    case_sensitive: bool = False
    cache_ttl_seconds: float = 0.0

    def __post_init__(self) -> None:
        self.freeze()
        return



DEFAULT_OVERLAY_DNS_ASPECTS = AspectsOverlayDNS()


__all__ = ["AspectsOverlayDNS", "DEFAULT_OVERLAY_DNS_ASPECTS"]
