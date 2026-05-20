"""
    .. module:: connectorinvocation
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains helper functions for composing argv
                   lists used to drive the ``twingate-connector`` CLI and the
                   surrounding ``systemctl`` service unit.

    The helpers in this module are pure functions — they do not invoke the
    command runner. They exist so the :class:`TwingateClient` body stays
    focused on aspects/elevation handling while argv composition can be unit
    tested independently.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os

from typing import List, Optional


CONNECTOR_BINARY = "twingate-connector"
CONNECTOR_SERVICE_NAME = "twingate-connector"
SYSTEMCTL_BINARY = "systemctl"


def compose_setup_argv(*, authkey: str, hostname: Optional[str] = None) -> List[str]:
    """
        Compose the argv list for the ``twingate-connector setup`` command.

        The ``authkey`` parameter is a combined token bundle expressed as
        ``"<access-token>:<refresh-token>"`` to keep the public ``IVPNClient``
        signature unchanged. The two halves are split and passed as separate
        flags to the connector binary.

        :param authkey: Combined ``"<access>:<refresh>"`` token bundle.
        :param hostname: Optional hostname to register with the control
            plane (passed as ``--name=<hostname>``).

        :returns: A list of argv elements.

        :raises: ValueError when ``authkey`` is empty or not in the expected
            ``"<access>:<refresh>"`` shape.
    """

    if authkey is None or len(authkey) == 0:
        err_msg_lines = [
            "A non-empty 'authkey' is required to compose the connector setup argv.",
            "EXPECTED SHAPE: '<access-token>:<refresh-token>'",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise ValueError(err_msg)

    if ":" not in authkey:
        err_msg_lines = [
            "The 'authkey' parameter must be a combined token bundle of shape '<access>:<refresh>'.",
            "RECEIVED: a string without a ':' separator (redacted).",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise ValueError(err_msg)

    access_token, refresh_token = authkey.split(":", 1)

    if len(access_token) == 0:
        err_msg_lines = [
            "The access-token half of 'authkey' is empty.",
            "EXPECTED SHAPE: '<access-token>:<refresh-token>'",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise ValueError(err_msg)

    if len(refresh_token) == 0:
        err_msg_lines = [
            "The refresh-token half of 'authkey' is empty.",
            "EXPECTED SHAPE: '<access-token>:<refresh-token>'",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise ValueError(err_msg)

    argv = [
        CONNECTOR_BINARY,
        "setup",
        f"--access-token={access_token}",
        f"--refresh-token={refresh_token}",
    ]

    if hostname is not None and len(hostname) > 0:
        argv.append(f"--name={hostname}")

    return argv


def compose_service_argv(*, action: str) -> List[str]:
    """
        Compose the argv list for a ``systemctl <action> twingate-connector``
        command.

        :param action: The systemctl verb (``start``, ``stop``, ``is-active``).

        :returns: A list of argv elements.

        :raises: ValueError when ``action`` is empty.
    """

    if action is None or len(action) == 0:
        err_msg_lines = [
            "A non-empty 'action' is required to compose the service argv.",
            "EXPECTED VALUES: 'start', 'stop', 'is-active'",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise ValueError(err_msg)

    argv = [SYSTEMCTL_BINARY, action, CONNECTOR_SERVICE_NAME]

    return argv


__all__ = [
    "CONNECTOR_BINARY",
    "CONNECTOR_SERVICE_NAME",
    "SYSTEMCTL_BINARY",
    "compose_setup_argv",
    "compose_service_argv",
]
