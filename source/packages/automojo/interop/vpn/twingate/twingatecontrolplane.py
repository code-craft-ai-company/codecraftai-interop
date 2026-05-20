"""
    .. module:: twingatecontrolplane
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Backward-compatibility re-export shim for the M3-landed
                   ``TwingateControlPlane`` class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The M3 ``TwingateControlPlane`` GraphQL admin client has been superseded
    by :class:`automojo.restclient.twingate.twingateclient.TwingateClient`,
    which lives in the dedicated ``automojo-restclient-twingate`` package
    landed in milestone M3b. ``TwingateClient`` is wire-compatible with the M3
    class — both implement
    :class:`automojo.interfaces.ivpncontrolplane.IVPNControlPlane`.

    This module is a thin shim retained for one release cycle. Importing it
    emits a :class:`DeprecationWarning` exactly once per process. The
    constructor signatures of the two classes match, so ``TwingateControlPlane``
    is exposed here as a plain alias of ``TwingateClient``. New code should
    import :class:`TwingateClient` directly from its new home.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.restclient.twingate.twingateclient import (
    TwingateClient, GRAPHQL_LEAF
)

from automojo.interop.vpn._shim import install_shim


install_shim(old_module=__name__,
             new_module="automojo.restclient.twingate.twingateclient")


# The M3 ``TwingateControlPlane`` and the M3b ``TwingateClient`` share the
# same constructor signature and implement the same ``IVPNControlPlane``
# protocol, so a plain alias is sufficient — no behavioural adaptation is
# required for legacy call sites.
TwingateControlPlane = TwingateClient


__all__ = ["TwingateControlPlane", "GRAPHQL_LEAF"]
