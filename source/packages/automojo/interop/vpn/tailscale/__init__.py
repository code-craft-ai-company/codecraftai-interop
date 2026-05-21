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


from typing import Any

from automojo.interop.vpn.tailscale.tailscaleclient import TailscaleClient


__all__ = ["TailscaleClient", "TailscaleControlPlane"]


def __getattr__(name: str) -> Any:
    """
        Lazily resolve the deprecated ``TailscaleControlPlane`` shim symbol so
        a plain ``import automojo.interop.vpn.tailscale`` does not fire the
        shim's :class:`DeprecationWarning`.

        :param name: The attribute being resolved.

        :returns: The resolved attribute value.

        :raises: :class:`AttributeError` when the name is not exported.
    """
    if name == "TailscaleControlPlane":
        from automojo.interop.vpn.tailscale.tailscalecontrolplane import (
            TailscaleControlPlane
        )
        rtnval = TailscaleControlPlane
        return rtnval

    err_msg = "module {!r} has no attribute {!r}".format(__name__, name)
    raise AttributeError(err_msg)
