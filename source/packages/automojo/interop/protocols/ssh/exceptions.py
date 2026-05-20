"""
    .. module:: exceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing SSH-specific exception types.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


class SSHAddressPlaneUnavailableError(Exception):
    """
        Raised when no requested address plane resolves to a non-empty
        address on the supplied :class:`IDeviceAddressSet`.

        This exception is the single failure shape of
        :func:`resolve_dial_target` and the ``device``-based variant of
        :meth:`SshBase.connect`. The message carries enough context (the
        device name and the full attempted plane sequence) to triage a
        connect failure without re-running with extra logging.
    """
    pass


__all__ = ["SSHAddressPlaneUnavailableError"]
