"""
    .. module:: tailscale
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tailscale-specific VPN interop implementations covering the
                   host-side daemon client and the REST control plane.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vpn.tailscale.tailscaleclient import TailscaleClient
from automojo.interop.vpn.tailscale.tailscalecontrolplane import TailscaleControlPlane


__all__ = ["TailscaleClient", "TailscaleControlPlane"]
