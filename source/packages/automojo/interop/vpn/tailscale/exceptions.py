"""
    .. module:: exceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module containing the typed exception hierarchy raised by
                   the Tailscale client and control plane interop classes.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional


class VPNBringUpError(Exception):
    """
        Raised when ``tailscale up`` returns a non-zero exit code.
    """

    def __init__(self, message: str, exit_code: Optional[int] = None,
                 stderr: Optional[str] = None):
        """
            Initialize the bring-up error with command exit context.

            :param message: A descriptive error message.
            :param exit_code: Exit code reported by the command runner.
            :param stderr: Captured stderr text from the command runner.

            :returns: ``None``.
        """
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr
        return


class VPNBringDownError(Exception):
    """
        Raised when ``tailscale down`` returns a non-zero exit code.
    """

    def __init__(self, message: str, exit_code: Optional[int] = None,
                 stderr: Optional[str] = None):
        """
            Initialize the bring-down error with command exit context.

            :param message: A descriptive error message.
            :param exit_code: Exit code reported by the command runner.
            :param stderr: Captured stderr text from the command runner.

            :returns: ``None``.
        """
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr
        return


class VPNStatusError(Exception):
    """
        Raised when ``tailscale status --json`` output cannot be parsed.
    """

    def __init__(self, message: str, raw_stdout: Optional[str] = None):
        """
            Initialize the status error with the raw stdout payload.

            :param message: A descriptive error message.
            :param raw_stdout: The raw stdout text that failed to parse.

            :returns: ``None``.
        """
        super().__init__(message)
        self.raw_stdout = raw_stdout
        return


class VPNControlPlaneAuthKeyError(Exception):
    """
        Raised when minting an auth key against the Tailscale control plane
        fails with a 4xx response.
    """

    def __init__(self, message: str, request_body: Optional[dict] = None,
                 response_body: Optional[str] = None,
                 status_code: Optional[int] = None):
        """
            Initialize the auth-key error with full request and response
            context.

            :param message: A descriptive error message.
            :param request_body: The dictionary sent as the POST body.
            :param response_body: The raw response body text from the API.
            :param status_code: The HTTP status code returned by the API.

            :returns: ``None``.
        """
        super().__init__(message)
        self.request_body = request_body
        self.response_body = response_body
        self.status_code = status_code
        return


class VPNControlPlaneQueryError(Exception):
    """
        Raised when a read query against the Tailscale control plane fails.
    """

    def __init__(self, message: str, response_body: Optional[str] = None,
                 status_code: Optional[int] = None):
        """
            Initialize the query error with response context.

            :param message: A descriptive error message.
            :param response_body: The raw response body text from the API.
            :param status_code: The HTTP status code returned by the API.

            :returns: ``None``.
        """
        super().__init__(message)
        self.response_body = response_body
        self.status_code = status_code
        return


class VPNControlPlaneMutationError(Exception):
    """
        Raised when a mutation (delete) against the Tailscale control plane
        fails with a non-2xx, non-404 response.
    """

    def __init__(self, message: str, response_body: Optional[str] = None,
                 status_code: Optional[int] = None):
        """
            Initialize the mutation error with response context.

            :param message: A descriptive error message.
            :param response_body: The raw response body text from the API.
            :param status_code: The HTTP status code returned by the API.

            :returns: ``None``.
        """
        super().__init__(message)
        self.response_body = response_body
        self.status_code = status_code
        return


class VPNControlPlaneACLError(Exception):
    """
        Raised when applying an ACL document via the Tailscale control plane
        fails.
    """

    def __init__(self, message: str, response_body: Optional[str] = None,
                 status_code: Optional[int] = None):
        """
            Initialize the ACL error with response context.

            :param message: A descriptive error message.
            :param response_body: The raw response body text from the API.
            :param status_code: The HTTP status code returned by the API.

            :returns: ``None``.
        """
        super().__init__(message)
        self.response_body = response_body
        self.status_code = status_code
        return
