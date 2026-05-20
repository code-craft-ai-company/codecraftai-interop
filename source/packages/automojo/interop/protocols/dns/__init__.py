"""
    .. module:: dns
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The dns package contains modules for engaging DNS operations and MDNS discovery operations.
    
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
from automojo.interop.protocols.dns.matchpredicate import is_match
from automojo.interop.protocols.dns.overlaydnsresolver import (
    OverlayDNSResolver,
    OverlayDNSResolverRegistry,
    KNOWN_OVERLAY_SUFFIXES,
)

