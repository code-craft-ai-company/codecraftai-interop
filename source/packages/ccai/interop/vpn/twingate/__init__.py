"""
    .. module:: twingate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Package containing the Twingate provider interop classes
                   (host-side connector client and GraphQL control plane).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any

from ccai.interop.vpn.twingate.twingateclient import TwingateClient
from ccai.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)


__all__ = [
    "TwingateClient",
    "TwingateControlPlane",
    "AspectsTwingate",
    "DEFAULT_TWINGATE_ASPECTS",
]


def __getattr__(name: str) -> Any:
    """
        Lazily resolve the deprecated ``TwingateControlPlane`` shim symbol so
        a plain ``import ccai.interop.vpn.twingate`` does not fire the
        shim's :class:`DeprecationWarning`.

        :param name: The attribute being resolved.

        :returns: The resolved attribute value.

        :raises: :class:`AttributeError` when the name is not exported.
    """
    if name == "TwingateControlPlane":
        from ccai.interop.vpn.twingate.twingatecontrolplane import (
            TwingateControlPlane
        )
        rtnval = TwingateControlPlane
        return rtnval

    err_msg = "module {!r} has no attribute {!r}".format(__name__, name)
    raise AttributeError(err_msg)
