"""
    .. module:: vpn
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing the host-side VPN interop clients grouped
                   by provider subpackage.  The control planes live in the
                   'codecraftai-restclient-tailscale' and
                   'codecraftai-restclient-twingate' packages.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.twingate.twingateclient import TwingateClient


__all__ = ["TwingateClient"]
