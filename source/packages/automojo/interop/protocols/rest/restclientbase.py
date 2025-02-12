
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List, Optional, Union

import os

from base64 import b64encode
from http import HTTPStatus

from requests import Session, Response, Request
from requests.adapters import HTTPAdapter

from automojo.errors.exceptions import HttpForbiddenError
from automojo.errors.raising import format_http_error_message, raise_for_http_status

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.basiccredential import BasicCredential

from automojo.interop.protocols.rest.aspectsrest import AspectsRest, LoggingPattern, DEFAULT_REST_ASPECTS

from automojo.interop.aspects import ActionPattern


class RestClientBase:
    """
        The :class:`RestClientBase` object is a generic REST client base object that can be inherited from
        in order to implement a REST client that utilizes 'aspects' based APIs
    """

    AUTH_LEAF = ""
    VERIFY_CERTIFICATE = False

    AUTHENTICATION_FAILURES = (HttpForbiddenError)

    def __init__(self, host: str, credential: BaseCredential, port: Optional[int] = None, scheme: Optional[str] = "https", aspects: AspectsRest = DEFAULT_REST_ASPECTS):
        self._host = host
        self._credential = credential
        self._aspects = aspects

        self._host_url = f"{scheme}://{self._host}"
        if port is not None:
            self._host_url = f"{self._host_url}:{port}"

        self._session: Session = None
        return
    
    @property
    def credential(self):
        return self._credential

    @property
    def host(self):
        return self._host
    

    def authenticate(self):
        """
            The `authenticate` method can be overloaded in order to modify the method of authentication
            for the rest client.  The current method of authentication is `Basic` authentication.
        """

        credential: BasicCredential = self._credential

        username = credential.username
        password = credential.password

        passwd_encoded =  b64encode(password).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {username}:{passwd_encoded}"
        }

        auth_leaf = self.AUTH_LEAF.rstrip("/")
        auth_url = f"{self._host_url}/{auth_leaf}"

        session = Session()

        resp: Response = session.post(auth_url, headers=headers, verify=self.VERIFY_CERTIFICATE)
        if resp.status_code != HTTPStatus.OK:
            errmsg_lines = [
                f"Error attempting to authenticate on url={auth_url}.",
                f"STATUS: {resp.status_code}"
                "RESPONSE:",
                resp.content
            ]
            errmsg = os.linesep.join(errmsg_lines)
            raise HttpForbiddenError(errmsg)

        self._session = session

        return


    def perform_call(self, *, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                     exp_status: Union[int, List[int]], headers: Optional[Dict[str, str]] = None,
                     context_msg: Optional[str] = None, aspects: Union[AspectsRest, None]) -> Response:
        
        if aspects is None:
            aspects = self._aspects

        response: Response = None

        action_pattern = aspects.action_pattern

        if action_pattern == ActionPattern.SINGLE_CALL:
            response = self._perform_single_call(leaf, method, params, body, exp_status, headers, context_msg, aspects)
        elif action_pattern == ActionPattern.SINGLE_CONNECTED_CALL:
            response = self._perform_single_connected_call(leaf, method, params, body, exp_status, headers, context_msg, aspects)
        elif action_pattern == ActionPattern.DO_UNTIL_CONNECTION_FAILURE:
            response = self._perform_call_until_connection_failure(leaf, method, params, body, exp_status, headers, context_msg, aspects)
        elif action_pattern == ActionPattern.DO_UNTIL_SUCCESS:
            response = self._perform_call_until_success(leaf, method, params, body, exp_status, headers, context_msg, aspects)
        elif action_pattern == ActionPattern.DO_WHILE_SUCCESS:
            response = self._perform_call_while_success(leaf, method, params, body, exp_status, headers, context_msg, aspects)
        else:
            errmsg = f"Unsupported action pattern '{action_pattern}'"
            raise RuntimeError(errmsg)

        return response


    def _format_call_url(self, leaf) -> str:

        call_url = f"{self._host_url}{leaf}"

        return call_url


    def _get_session(self, aspects: AspectsRest) -> Session:

        session = None

        if aspects.session is not None:
            session = aspects.session
        else:
            if self._session is None:
                self.authenticate()

            session = self._session

        return session


    def _perform_single_call(self, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                             exp_status: Union[int, List[int]], headers: Union[Dict[str, str], None],
                             context_msg: Union[str, None], aspects: AspectsRest) -> Response:
        
        call_url = self._format_call_url(leaf)

        logger = aspects.logger

        connection_timeout: float = aspects.connection_timeout
        monitor_delay: float = aspects.monitor_delay
        allowed_error_codes: List[int] = aspects.allowed_error_codes
        allowed_connection_exceptions: List[BaseException] = aspects.allowed_connection_exceptions

        auth_retry = False
        while True:

            try:
                session: Session = self._get_session(aspects)

                req = Request(method=method, url=call_url, params=params, data=body)
                
                resp :Response = session.send(req, timeout=connection_timeout)

            except self.AUTHENTICATION_FAILURES as autherr:
                if not auth_retry:
                    self._session = None
                else:
                    break # Only allow one authentication retry

            else:
                break

        found_status = resp.status_code
        if found_status != exp_status:
            resp_content = resp.content

            errmsg = format_http_error_message(found_status, resp_content, call_url, context=context_msg)
            logger.error(errmsg)

            raise_for_http_status(found_status, resp_content, call_url, context=context_msg)

        return resp
    

    def _perform_single_connected_call(self, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                                       exp_status: Union[int, List[int]], headers: Union[Dict[str, str], None],
                                       context_msg: Union[str, None], aspects: AspectsRest) -> Response:
        
        call_url = self._format_call_url(leaf)

        logger = aspects.logger

        completion_timeout: float = aspects.completion_timeout
        completion_interval: float = aspects.completion_interval
        connection_timeout: float = aspects.connection_timeout
        connection_interval: float = aspects.connection_interval
        inactivity_timeout: float = aspects.inactivity_timeout
        inactivity_interval: float = aspects.inactivity_interval
        monitor_delay: float = aspects.monitor_delay
        logging_pattern: LoggingPattern = aspects.logging_pattern
        retry_logging_interval: int = aspects.retry_logging_interval
        allowed_error_codes: List[int] = aspects.allowed_error_codes
        allowed_connection_exceptions: List[BaseException] = aspects.allowed_connection_exceptions
        must_connect: bool = aspects.must_connect

        return
    

    def _perform_call_until_connection_failure(self, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                                               exp_status: Union[int, List[int]], headers: Union[Dict[str, str], None],
                                               context_msg: Union[str, None], aspects: AspectsRest) -> Response:
        
        call_url = self._format_call_url(leaf)

        logger = aspects.logger

        completion_timeout: float = aspects.completion_timeout
        completion_interval: float = aspects.completion_interval
        connection_timeout: float = aspects.connection_timeout
        connection_interval: float = aspects.connection_interval
        inactivity_timeout: float = aspects.inactivity_timeout
        inactivity_interval: float = aspects.inactivity_interval
        monitor_delay: float = aspects.monitor_delay
        logging_pattern: LoggingPattern = aspects.logging_pattern
        retry_logging_interval: int = aspects.retry_logging_interval
        allowed_error_codes: List[int] = aspects.allowed_error_codes
        allowed_connection_exceptions: List[BaseException] = aspects.allowed_connection_exceptions
        must_connect: bool = aspects.must_connect
        
        return
    

    def _perform_call_until_success(self, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                                    exp_status: Union[int, List[int]], headers: Union[Dict[str, str], None],
                                    context_msg: Union[str, None], aspects: AspectsRest) -> Response:
        
        call_url = self._format_call_url(leaf)

        logger = aspects.logger

        completion_timeout: float = aspects.completion_timeout
        completion_interval: float = aspects.completion_interval
        connection_timeout: float = aspects.connection_timeout
        connection_interval: float = aspects.connection_interval
        inactivity_timeout: float = aspects.inactivity_timeout
        inactivity_interval: float = aspects.inactivity_interval
        monitor_delay: float = aspects.monitor_delay
        logging_pattern: LoggingPattern = aspects.logging_pattern
        retry_logging_interval: int = aspects.retry_logging_interval
        allowed_error_codes: List[int] = aspects.allowed_error_codes
        allowed_connection_exceptions: List[BaseException] = aspects.allowed_connection_exceptions
        must_connect: bool = aspects.must_connect

        return
    

    def _perform_call_while_success(self, leaf: str, method: str, params: Union[Dict[str, str], None], body: Union[Dict[str, str], None],
                                    exp_status: Union[int, List[int]], headers: Union[Dict[str, str], None],
                                    context_msg: Union[str, None], aspects: AspectsRest) -> Response:
        
        call_url = self._format_call_url(leaf)

        logger = aspects.logger

        completion_timeout: float = aspects.completion_timeout
        completion_interval: float = aspects.completion_interval
        connection_timeout: float = aspects.connection_timeout
        connection_interval: float = aspects.connection_interval
        inactivity_timeout: float = aspects.inactivity_timeout
        inactivity_interval: float = aspects.inactivity_interval
        monitor_delay: float = aspects.monitor_delay
        logging_pattern: LoggingPattern = aspects.logging_pattern
        retry_logging_interval: int = aspects.retry_logging_interval
        allowed_error_codes: List[int] = aspects.allowed_error_codes
        allowed_connection_exceptions: List[BaseException] = aspects.allowed_connection_exceptions
        must_connect: bool = aspects.must_connect

        return
    
