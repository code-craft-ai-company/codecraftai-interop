"""
    .. module:: tailscale
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tailscale-specific VPN interop implementation of the
                   host-side daemon client.  The REST control plane lives in
                   the 'codecraftai-restclient-tailscale' package
                   (ccai.restclient.tailscale).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.tailscale.tailscaleclient import TailscaleClient


__all__ = ["TailscaleClient"]
