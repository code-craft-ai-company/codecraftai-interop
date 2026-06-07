"""
    .. module:: exceptions
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the error types utilized by the multicast DNS code.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from ccai.errors.exceptions import ProtocolError

class DnsProtocolError(ProtocolError):
    """
        Base error for all DNS protocol errors.
    """

class DnsDecodeError(DnsProtocolError):
    """
        Error raised when the decoding of a DNS response fails.
    """
class DnsNonUniqueNameError(DnsProtocolError):
    """
        A non-unique name was encountered.
    """

class DnsNamePartTooLongError(DnsProtocolError):
    """
        The name part was too long
    """

class DnsBadTypeInNameError(DnsProtocolError):
    """
        Bad type in name
    """

class OverlayDNSError(DnsProtocolError):
    """
        Raised when an underlying overlay provider call fails irrecoverably
        during overlay-plane resolution.
    """

class OverlayDNSNoMatchError(DnsProtocolError):
    """
        Raised by :class:`OverlayDNSResolver` when no overlay or fall-through
        resolution succeeds and fall-through to the standard system resolver
        is disabled.
    """
