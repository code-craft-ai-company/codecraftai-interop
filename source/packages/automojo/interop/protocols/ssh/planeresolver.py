"""
    .. module:: planeresolver
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the pure :func:`resolve_dial_target`
                   helper used by :class:`SshBase` to choose the dial
                   target address from an :class:`IDeviceAddressSet`.

    The resolver is intentionally network-free: it consumes only data
    structures and an :class:`AddressPlane` selection so it can be
    property-tested without mocking the network.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os

from typing import List, Optional, Sequence

from automojo.interfaces.addressplane import AddressPlane, IDeviceAddressSet

from automojo.interop.protocols.ssh.exceptions import SSHAddressPlaneUnavailableError


def resolve_dial_target(*, address_set: IDeviceAddressSet, preferred_plane: AddressPlane,
                        fallback_planes: Optional[Sequence[AddressPlane]] = None,
                        device_name: Optional[str] = None) -> str:
    """
        Resolve the dial target address from an :class:`IDeviceAddressSet`.

        The algorithm tries ``preferred_plane`` first, then each plane in
        ``fallback_planes`` in declared order. The first plane whose
        :meth:`IDeviceAddressSet.address_for` returns a non-``None``,
        non-empty string is returned. An empty string is treated as
        absent.

        :param address_set: The device's address set to resolve against.
        :param preferred_plane: The preferred plane to attempt first.
        :param fallback_planes: An optional ordered sequence of planes to
            try when ``preferred_plane`` is unavailable. ``None`` disables
            fall-through.
        :param device_name: Optional device identifier used in the error
            message when no plane resolves.

        :returns: The resolved non-empty address string.

        :raises SSHAddressPlaneUnavailableError: When neither the preferred
            plane nor any fallback plane resolves to a non-empty address.
    """
    if address_set is None:
        raise SSHAddressPlaneUnavailableError("address_set is required for plane resolution") from None

    attempted: List[AddressPlane] = [preferred_plane]
    if fallback_planes is not None:
        for plane in fallback_planes:
            attempted.append(plane)

    skipped: List[AddressPlane] = []
    resolved: Optional[str] = None
    for plane in attempted:
        candidate = address_set.address_for(plane=plane)
        if candidate is not None and len(candidate) > 0:
            resolved = candidate
            break
        skipped.append(plane)

    if resolved is None:
        dev_label = device_name
        if dev_label is None:
            dev_label = "<unnamed-device>"
        attempted_labels = [p.name for p in attempted]
        err_msg_lines = [
            "No usable address plane resolved for device '{}'.".format(dev_label),
            "ATTEMPTED PLANES (in order):"
        ]
        for label in attempted_labels:
            err_msg_lines.append("    - {}".format(label))
        err_msg = os.linesep.join(err_msg_lines)
        raise SSHAddressPlaneUnavailableError(err_msg) from None

    return resolved


def skipped_planes(*, address_set: IDeviceAddressSet, preferred_plane: AddressPlane,
                   fallback_planes: Optional[Sequence[AddressPlane]] = None) -> List[AddressPlane]:
    """
        Enumerate the planes that would be skipped before the first
        resolved plane (used by callers to emit WARNING log lines).

        The function is pure and matches the iteration order of
        :func:`resolve_dial_target`. If no plane resolves it returns the
        full attempted list.

        :param address_set: The device's address set to inspect.
        :param preferred_plane: The preferred plane considered first.
        :param fallback_planes: Optional ordered fallback planes.

        :returns: The list of planes skipped before resolution. Empty
            when the preferred plane resolves on the first try.
    """
    attempted: List[AddressPlane] = [preferred_plane]
    if fallback_planes is not None:
        for plane in fallback_planes:
            attempted.append(plane)

    skipped: List[AddressPlane] = []
    for plane in attempted:
        candidate = address_set.address_for(plane=plane)
        if candidate is not None and len(candidate) > 0:
            break
        skipped.append(plane)

    return skipped


__all__ = ["resolve_dial_target", "skipped_planes"]
