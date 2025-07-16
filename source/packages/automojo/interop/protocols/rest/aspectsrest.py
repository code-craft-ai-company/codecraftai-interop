
"""
    .. module:: aspectsrest
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: aspectsrest module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, Union

import logging

from requests import Session

from automojo.interop.aspects import (
    Aspects,
    ActionPattern,
    LoggingPattern,
    DEFAULT_COMPLETION_TIMEOUT,
    DEFAULT_COMPLETION_INTERVAL,
    DEFAULT_CONNECTION_TIMEOUT,
    DEFAULT_CONNECTION_INTERVAL,
    DEFAULT_INACTIVITY_TIMEOUT,
    DEFAULT_INACTIVITY_INTERVAL,
    DEFAULT_MONITOR_DELAY,
    DEFAULT_LOGGING_PATTERN,
    DEFAULT_RETRY_LOGGING_INTERVAL,
    DEFAULT_ALLOWED_ERROR_CODES,
    DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
    DEFAULT_MUST_CONNECT
)

class AspectsRest(Aspects):
    """
        Aspects container specialized for REST operations.
    """
    def __init__(self, *, action_pattern: ActionPattern = ActionPattern.SINGLE_CALL,
                completion_timeout: float = DEFAULT_COMPLETION_TIMEOUT,
                completion_interval: float = DEFAULT_COMPLETION_INTERVAL,
                connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
                inactivity_timeout: float = DEFAULT_INACTIVITY_TIMEOUT,
                monitor_delay: float = DEFAULT_MONITOR_DELAY,
                logging_pattern: LoggingPattern = DEFAULT_LOGGING_PATTERN,
                retry_logging_interval: int = DEFAULT_RETRY_LOGGING_INTERVAL,
                allowed_error_codes: List[int] = DEFAULT_ALLOWED_ERROR_CODES,
                allowed_connection_exceptions: List[BaseException] = DEFAULT_ALLOWED_CONNECTION_EXCEPTIONS,
                must_connect: bool = DEFAULT_MUST_CONNECT,
                logger: Optional[logging.Logger]=None,
                session: Optional[Session] = None):
        """
            Initialize a set of REST call aspects.

            :param action_pattern: Default action pattern for calls.
            :param completion_timeout: Time in seconds to wait for completion.
            :param completion_interval: Polling interval when waiting.
            :param connection_timeout: Timeout for establishing connections.
            :param inactivity_timeout: Timeout for inactivity in seconds.
            :param monitor_delay: Delay before monitoring begins.
            :param logging_pattern: Pattern used for call logging.
            :param retry_logging_interval: Interval for retry log messages.
            :param allowed_error_codes: HTTP status codes considered success.
            :param allowed_connection_exceptions: Exceptions allowed during connect.
            :param must_connect: Whether a connection must be established.
            :param logger: Logger to use for messages.
            :param session: Requests session to reuse.
        """
        super().__init__(
            action_pattern=action_pattern,
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
            logger=logger,
        )
        self._session = session
        return
    
    @property
    def session(self) -> Union[Session, None]:
        """
            Requests :class:`Session` object associated with the aspects.

            :returns: A :class:`requests.Session` or ``None``.
        """
        return self._session



DEFAULT_REST_ASPECTS = AspectsRest()

