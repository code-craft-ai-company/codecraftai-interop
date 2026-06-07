"""
    .. module:: exceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that re-exports the shared VPN interop exceptions
                   used by the Twingate connector client and control plane.

    The shared exception hierarchy lives next to the Tailscale interop classes
    in :mod:`ccai.interop.vpn.tailscale.exceptions`. The Twingate
    subpackage re-exports those types so consumers can import them from a
    Twingate-local module without coupling test code to a sibling provider's
    module path.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.tailscale.exceptions import (
    VPNBringUpError,
    VPNBringDownError,
    VPNStatusError,
    VPNControlPlaneAuthKeyError,
    VPNControlPlaneQueryError,
    VPNControlPlaneMutationError,
    VPNControlPlaneACLError,
)


__all__ = [
    "VPNBringUpError",
    "VPNBringDownError",
    "VPNStatusError",
    "VPNControlPlaneAuthKeyError",
    "VPNControlPlaneQueryError",
    "VPNControlPlaneMutationError",
    "VPNControlPlaneACLError",
]
