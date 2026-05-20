"""
    .. module:: aspectstwingate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AspectsTwingate` class used
                   to control behaviour of Twingate GraphQL control-plane calls.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional, Tuple

import logging

from requests import Session

from automojo.restclient.base.aspectsrest import (
    ActionPattern, AspectsRest, LoggingPattern,
    DEFAULT_COMPLETION_TIMEOUT, DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_CONNECTION_TIMEOUT, DEFAULT_INACTIVITY_TIMEOUT,
    DEFAULT_MONITOR_DELAY, DEFAULT_RETRY_LOGGING_INTERVAL,
    DEFAULT_LOGGING_PATTERN, DEFAULT_MUST_CONNECT,
    DEFAULT_ALLOWED_ERROR_CODES, DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
)


DEFAULT_MUTATION_DEPENDENCY_PAUSE_SECONDS = 0.5


class AspectsTwingate(AspectsRest):
    """
        :class:`AspectsTwingate` extends :class:`AspectsRest` with a
        Twingate-specific knob — ``mutation_dependency_pause_seconds`` —
        used by :meth:`TwingateControlPlane.apply_acl` to space out
        dependent mutations when the Twingate API surfaces eventual
        consistency lag.
    """

    def __init__(self, *,
                 action_pattern: ActionPattern = ActionPattern.SINGLE_CALL,
                 completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                 completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                 connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
                 inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                 monitor_delay: float = DEFAULT_MONITOR_DELAY,
                 logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                 retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                 allowed_error_codes: Tuple[int, ...] = DEFAULT_ALLOWED_ERROR_CODES,
                 allowed_connection_exceptions: Tuple[BaseException, ...] = DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
                 must_connect: bool = DEFAULT_MUST_CONNECT,
                 logger: Optional[logging.Logger] = None,
                 session: Optional[Session] = None,
                 mutation_dependency_pause_seconds: float = DEFAULT_MUTATION_DEPENDENCY_PAUSE_SECONDS):
        """
            Initialize a Twingate-specific aspects bundle.

            :param mutation_dependency_pause_seconds: Pause between dependent
                mutation phases inside ``apply_acl`` to accommodate eventual
                consistency.

            :returns: ``None``.
        """
        # The base AspectsRest freezes itself at the end of its __init__;
        # we must add our own attribute prior to that freeze. We piggyback by
        # temporarily flipping the frozen flag after super().__init__().
        super().__init__(
            action_pattern=action_pattern,
            completion_timeout=completion_timeout,
            completion_interval=completion_interval,
            connection_timeout=connection_timeout,
            inactivity_timeout=inactivity_timeout,
            monitor_delay=monitor_delay,
            logging_pattern=logging_pattern,
            retry_logging_interval=retry_logging_interval,
            allowed_error_codes=allowed_error_codes,
            allowed_connection_exceptions=allowed_connection_exceptions,
            must_connect=must_connect,
            logger=logger,
            session=session,
        )

        object.__setattr__(self, "__frozen__", False)
        self.mutation_dependency_pause_seconds = mutation_dependency_pause_seconds
        object.__setattr__(self, "__frozen__", True)
        return


DEFAULT_TWINGATE_ASPECTS = AspectsTwingate()


__all__ = [
    "AspectsTwingate",
    "DEFAULT_TWINGATE_ASPECTS",
    "DEFAULT_MUTATION_DEPENDENCY_PAUSE_SECONDS",
]
