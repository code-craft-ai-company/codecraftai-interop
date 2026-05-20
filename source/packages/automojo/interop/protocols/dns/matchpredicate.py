"""
    .. module:: matchpredicate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the pure :func:`is_match` predicate
                   used by :class:`OverlayDNSResolver` to decide whether a
                   query string matches a given :class:`OverlayCandidate`.

    The predicate is a total, deterministic function of its inputs. It
    performs no I/O, consults no clock, environment, or random state, and
    never raises. Property tests under
    ``test_matchpredicate_properties.py`` assert these invariants.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.protocols.dns.aspectsoverlaydns import (
    AspectsOverlayDNS,
    DEFAULT_OVERLAY_DNS_ASPECTS,
)
from automojo.interop.protocols.dns.overlaycandidate import OverlayCandidate


def _normalize(*, value: str, case_sensitive: bool) -> str:
    """
        Normalise a string for matching by folding case when configured.

        :param value: The input string to normalise.
        :param case_sensitive: When ``False`` the value is lower-cased.

        :returns: The normalised string.
    """
    if case_sensitive:
        rtnval = value
    else:
        rtnval = value.lower()
    return rtnval


def is_match(
    *,
    query: str,
    candidate: OverlayCandidate,
    aspects: AspectsOverlayDNS = DEFAULT_OVERLAY_DNS_ASPECTS,
) -> bool:
    """
        Pure, total, deterministic predicate testing whether ``query``
        names ``candidate``.

        Match rules:

        1. Both ``query`` and the candidate's name fields are folded to
           lowercase unless ``aspects.case_sensitive`` is ``True``.
        2. The candidate matches when ``query`` equals
           ``candidate.short_hostname``.
        3. The candidate matches when ``candidate.magicdns_name`` is
           non-empty and starts with ``query`` followed by ``"."``.
        4. The candidate also matches when ``query`` equals
           ``candidate.magicdns_name`` exactly (the full FQDN form).
        5. Otherwise the candidate does not match.

        The predicate never raises and never performs I/O.

        :param query: The name being resolved.
        :param candidate: The candidate record to test against.
        :param aspects: Behaviour control; only ``case_sensitive`` is read.

        :returns: ``True`` when ``candidate`` names ``query``, otherwise
            ``False``.
    """

    if not isinstance(query, str):
        rtnval = False
        return rtnval

    if not isinstance(candidate, OverlayCandidate):
        rtnval = False
        return rtnval

    case_sensitive = aspects.case_sensitive

    norm_query = _normalize(value=query, case_sensitive=case_sensitive)

    short_hostname = candidate.short_hostname
    if not isinstance(short_hostname, str):
        short_hostname = ""

    norm_short = _normalize(value=short_hostname, case_sensitive=case_sensitive)

    if len(norm_query) > 0 and norm_query == norm_short:
        rtnval = True
        return rtnval

    magicdns_name = candidate.magicdns_name
    if magicdns_name is None:
        magicdns_name = ""
    if not isinstance(magicdns_name, str):
        magicdns_name = ""

    norm_magic = _normalize(value=magicdns_name, case_sensitive=case_sensitive)

    if len(norm_query) > 0 and len(norm_magic) > 0:
        if norm_query == norm_magic:
            rtnval = True
            return rtnval

        prefix = norm_query + "."
        if norm_magic.startswith(prefix):
            rtnval = True
            return rtnval

    rtnval = False
    return rtnval


__all__ = ["is_match"]
