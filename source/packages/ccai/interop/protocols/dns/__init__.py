"""
    .. module:: dns
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The dns package contains modules for engaging DNS operations and MDNS discovery operations.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.protocols.dns.aspectsoverlaydns import (
    AspectsOverlayDNS,
    DEFAULT_OVERLAY_DNS_ASPECTS,
)
from ccai.interop.protocols.dns.overlaycandidate import OverlayCandidate
from ccai.interop.protocols.dns.matchpredicate import is_match
from ccai.interop.protocols.dns.overlaydnsresolver import (
    OverlayDNSResolver,
    OverlayDNSResolverRegistry,
    KNOWN_OVERLAY_SUFFIXES,
)

