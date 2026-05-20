"""
    .. module:: vpn
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing VPN interop clients and control plane
                   implementations grouped by provider subpackage.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vpn.twingate.twingateclient import TwingateClient
from automojo.interop.vpn.twingate.twingatecontrolplane import TwingateControlPlane


__all__ = ["TwingateClient", "TwingateControlPlane"]
