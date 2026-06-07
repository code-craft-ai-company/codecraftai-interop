"""
    .. module:: aspectsvpnclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AspectsVPNClient` class used
                   to control behaviour of VPN client interop calls.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Optional, Tuple

import logging

from ccai.interop.aspects import (
    Aspects, ActionPattern, LoggingPattern,
    DEFAULT_COMPLETION_TIMEOUT, DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_CONNECTION_TIMEOUT, DEFAULT_CONNECTION_INTERVAL,
    DEFAULT_INACTIVITY_TIMEOUT, DEFAULT_INACTIVITY_INTERVAL,
    DEFAULT_MONITOR_DELAY, DEFAULT_RETRY_LOGGING_INTERVAL,
    DEFAULT_LOGGING_PATTERN, DEFAULT_MUST_CONNECT,
    DEFAULT_ALLOWED_ERROR_CODES, DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS
)


DEFAULT_VPN_COMMAND_TIMEOUT_SECONDS = 30
DEFAULT_VPN_STATUS_REFRESH_SECONDS = 10


class AspectsVPNClient(Aspects):
    """
        :class:`AspectsVPNClient` extends :class:`Aspects` with VPN-specific
        behaviour controls used by host-side mesh-VPN clients.

        The added knobs are kept independent of the generic interop aspects so
        callers can tune VPN command behaviour without disturbing other
        protocol aspects in shared code paths.
    """

    def __init__(self, action_pattern: ActionPattern = ActionPattern.SINGLE_CALL,
                 completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                 completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                 connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
                 connection_interval: float = DEFAULT_CONNECTION_INTERVAL,
                 inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                 inactivity_interval: float = DEFAULT_INACTIVITY_INTERVAL,
                 monitor_delay: float = DEFAULT_MONITOR_DELAY,
                 logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                 retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                 allowed_error_codes: Tuple[int, ...] = DEFAULT_ALLOWED_ERROR_CODES,
                 allowed_connection_exceptions: Tuple[BaseException, ...] = DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
                 must_connect: bool = DEFAULT_MUST_CONNECT,
                 logger: Optional[logging.Logger] = None,
                 dry_run: bool = False,
                 elevated: bool = False,
                 command_timeout_seconds: float = DEFAULT_VPN_COMMAND_TIMEOUT_SECONDS,
                 status_refresh_seconds: float = DEFAULT_VPN_STATUS_REFRESH_SECONDS):
        """
            Initialize a set of VPN client aspects.

            :param dry_run: When ``True``, behaviour-bearing calls SHALL NOT
                invoke the command runner and SHALL return a sentinel status.
            :param elevated: When ``True``, write operations SHALL run via the
                command runner with ``elevated=True``.
            :param command_timeout_seconds: Per-command timeout passed to the
                command runner.
            :param status_refresh_seconds: Maximum age of a cached
                ``VPNStatus`` before a refresh SHALL be triggered.

            :returns: ``None``.
        """
        super().__init__(action_pattern=action_pattern,
                         completion_timeout=completion_timeout,
                         completion_interval=completion_interval,
                         connection_timeout=connection_timeout,
                         connection_interval=connection_interval,
                         inactivity_timeout=inactivity_timeout,
                         inactivity_interval=inactivity_interval,
                         monitor_delay=monitor_delay,
                         logging_pattern=logging_pattern,
                         retry_logging_interval=retry_logging_interval,
                         allowed_error_codes=allowed_error_codes,
                         allowed_connection_exceptions=allowed_connection_exceptions,
                         must_connect=must_connect,
                         logger=logger)

        # Parent Aspects.__init__ freezes the instance; unfreeze, attach the
        # VPN-specific knobs, then re-freeze to preserve immutability.
        object.__setattr__(self, "__frozen__", False)
        self._dry_run = dry_run
        self._elevated = elevated
        self._command_timeout_seconds = command_timeout_seconds
        self._status_refresh_seconds = status_refresh_seconds
        self.freeze()
        return

    @property
    def dry_run(self) -> bool:
        """
            Whether the call is in dry-run mode and SHALL NOT execute commands.

            :returns: ``True`` when dry-run is requested.
        """
        rtnval = self._dry_run
        return rtnval

    @property
    def elevated(self) -> bool:
        """
            Whether write operations SHALL be run elevated.

            :returns: ``True`` when elevation is requested.
        """
        rtnval = self._elevated
        return rtnval

    @property
    def command_timeout_seconds(self) -> float:
        """
            Per-command timeout in seconds.

            :returns: A timeout value in seconds.
        """
        rtnval = self._command_timeout_seconds
        return rtnval

    @property
    def status_refresh_seconds(self) -> float:
        """
            Maximum age of a cached status snapshot in seconds.

            :returns: A refresh window in seconds.
        """
        rtnval = self._status_refresh_seconds
        return rtnval


DEFAULT_VPN_CLIENT_ASPECTS = AspectsVPNClient()
