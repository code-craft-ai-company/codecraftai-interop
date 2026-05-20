"""
    .. module:: twingate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing the Twingate provider interop classes
                   (host-side connector client and GraphQL control plane).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vpn.twingate.twingateclient import TwingateClient
from automojo.interop.vpn.twingate.twingatecontrolplane import TwingateControlPlane
from automojo.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)


__all__ = [
    "TwingateClient",
    "TwingateControlPlane",
    "AspectsTwingate",
    "DEFAULT_TWINGATE_ASPECTS",
]
