"""
    .. module:: vpn
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing VPN interop clients and control plane
                   implementations grouped by provider subpackage.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any

from ccai.interop.vpn.twingate.twingateclient import TwingateClient


__all__ = ["TwingateClient"]


def __getattr__(name: str) -> Any:
    """
        Lazily resolve the deprecated control-plane shim symbols so that a
        plain ``import ccai.interop.vpn`` does not fire the shim's
        :class:`DeprecationWarning`. The warning fires only on a genuine
        legacy access of the deprecated name.

        :param name: The attribute being resolved.

        :returns: The resolved attribute value.

        :raises: :class:`AttributeError` when the name is not exported.
    """
    if name == "TwingateControlPlane":
        try:
            from ccai.interop.vpn.twingate.twingatecontrolplane import (
                TwingateControlPlane
            )
        except ImportError as ierr:
            err_msg = (
                "TwingateControlPlane is a deprecated shim that now requires the "
                "'codecraftai-restclient-twingate' package (ccai.restclient.twingate). "
                "Install it, or migrate to ccai.restclient.twingate.twingateclient.TwingateClient."
            )
            raise ImportError(err_msg) from ierr
        rtnval = TwingateControlPlane
        return rtnval

    err_msg = "module {!r} has no attribute {!r}".format(__name__, name)
    raise AttributeError(err_msg)
