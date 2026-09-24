"""
    .. module:: twingate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing the Twingate provider interop classes
                   (host-side connector client).  The GraphQL control plane
                   lives in the 'codecraftai-restclient-twingate' package
                   (ccai.restclient.twingate).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.twingate.twingateclient import TwingateClient
from ccai.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)


__all__ = [
    "TwingateClient",
    "AspectsTwingate",
    "DEFAULT_TWINGATE_ASPECTS",
]
