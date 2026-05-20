"""
    .. module:: twingateclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TwingateClient` host-side
                   driver for the Twingate connector service.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import logging
import os

from typing import Dict, List, Optional

from automojo.interfaces.icommandrunner import ICommandRunner, RunResult
from automojo.interfaces.ivpnclient import VPNStatus

from automojo.interop.vpn.aspectsvpnclient import (
    AspectsVPNClient, DEFAULT_VPN_CLIENT_ASPECTS
)
from automojo.interop.vpn.twingate.connectorinvocation import (
    compose_setup_argv, compose_service_argv
)
from automojo.interop.vpn.twingate.exceptions import (
    VPNBringUpError, VPNBringDownError
)


PROVIDER_NAME = "twingate"

_PEER_ENUMERATION_WARNING_EMITTED = False


class TwingateClient:
    """
        :class:`TwingateClient` drives the local Twingate connector service
        through an injected :class:`ICommandRunner` and conforms to the
        :class:`IVPNClient` protocol.

        Provider asymmetry — by design, not a TODO:

        * Twingate connector hosts are not assigned an overlay IP. The
          :meth:`self_address` accessor returns ``None`` unconditionally.
        * Twingate is resource-scoped rather than flat-mesh. Peer enumeration
          belongs to the control plane (resource discovery) rather than the
          local daemon, so :meth:`peer_addresses` returns an empty mapping
          and logs a process-once DEBUG message.

        Behaviour-bearing methods accept an :class:`AspectsVPNClient`
        instance. There are no behaviour-modifying decorators.
    """

    def __init__(self, *, command_runner: ICommandRunner,
                 file_operator: Optional[object] = None,
                 aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS):
        """
            Initialize the Twingate connector client.

            :param command_runner: The :class:`ICommandRunner` used to invoke
                ``twingate-connector`` and ``systemctl``.
            :param file_operator: Optional file operator handle reserved for
                future connector-config tooling. Unused today; accepted to
                match the cross-provider constructor shape.
            :param aspects: The default :class:`AspectsVPNClient` to use when
                a caller does not supply one.

            :returns: ``None``.
        """
        self._command_runner = command_runner
        self._file_operator = file_operator
        self._default_aspects = aspects
        self._logger = logging.getLogger(__name__)
        self._last_status: Optional[VPNStatus] = None
        return

    @property
    def command_runner(self) -> ICommandRunner:
        """
            Return the injected command runner.

            :returns: The :class:`ICommandRunner` supplied at construction time.
        """
        rtnval = self._command_runner
        return rtnval

    @property
    def aspects(self) -> AspectsVPNClient:
        """
            Return the default aspects for this client.

            :returns: The :class:`AspectsVPNClient` supplied at construction time.
        """
        rtnval = self._default_aspects
        return rtnval

    def bring_up(self, *, authkey: str, hostname: Optional[str] = None,
                 advertise_tags: Optional[List[str]] = None,
                 aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> VPNStatus:
        """
            Register the connector with the Twingate network and start its
            service unit.

            :param authkey: Combined ``"<access-token>:<refresh-token>"``
                connector token bundle.
            :param hostname: Optional hostname to register with the control
                plane (passed as ``--name=<hostname>``).
            :param advertise_tags: Tags to advertise. Twingate does not
                consume tags at the daemon layer; the value is echoed back
                on the returned :class:`VPNStatus` for caller consistency.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`VPNStatus` reflecting the post-bring-up
                state.

            :raises: :class:`VPNBringUpError` when either the ``setup`` or
                ``start`` command exits non-zero.
            :raises: ValueError when ``authkey`` is malformed.
        """

        if authkey is None or len(authkey) == 0:
            err_msg_lines = [
                "TwingateClient.bring_up requires a non-empty 'authkey'.",
                "EXPECTED SHAPE: '<access-token>:<refresh-token>'",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise ValueError(err_msg)

        tags_for_status = []
        if advertise_tags is not None:
            tags_for_status = list(advertise_tags)

        if aspects.dry_run:
            rtnval = VPNStatus(
                connected=False,
                backend_state="dry-run",
                self_address=None,
                hostname=hostname,
                tags=tags_for_status,
                provider=PROVIDER_NAME,
            )
            self._last_status = rtnval
            return rtnval

        setup_argv = compose_setup_argv(authkey=authkey, hostname=hostname)
        start_argv = compose_service_argv(action="start")

        elevated = aspects.elevated
        timeout_seconds = aspects.command_timeout_seconds

        setup_result: RunResult = self._command_runner.run(
            setup_argv,
            elevated=elevated,
            timeout=timeout_seconds,
        )

        if setup_result.exit_code != 0:
            err_msg_lines = [
                "Twingate connector 'setup' command failed.",
                f"ARGV: {setup_argv}",
                f"EXIT_CODE: {setup_result.exit_code}",
                "STDERR:",
                setup_result.stderr if setup_result.stderr is not None else "",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNBringUpError(
                err_msg,
                exit_code=setup_result.exit_code,
                stderr=setup_result.stderr,
            )

        start_result: RunResult = self._command_runner.run(
            start_argv,
            elevated=elevated,
            timeout=timeout_seconds,
        )

        if start_result.exit_code != 0:
            err_msg_lines = [
                "Twingate connector service 'start' command failed.",
                f"ARGV: {start_argv}",
                f"EXIT_CODE: {start_result.exit_code}",
                "STDERR:",
                start_result.stderr if start_result.stderr is not None else "",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNBringUpError(
                err_msg,
                exit_code=start_result.exit_code,
                stderr=start_result.stderr,
            )

        rtnval = VPNStatus(
            connected=True,
            backend_state="Connected",
            self_address=None,
            hostname=hostname,
            tags=tags_for_status,
            provider=PROVIDER_NAME,
        )
        self._last_status = rtnval
        return rtnval

    def bring_down(self, *,
                   aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> None:
        """
            Stop the local Twingate connector service unit.

            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`VPNBringDownError` when the stop command exits
                non-zero.
        """

        if aspects.dry_run:
            return None

        stop_argv = compose_service_argv(action="stop")

        elevated = aspects.elevated
        timeout_seconds = aspects.command_timeout_seconds

        stop_result: RunResult = self._command_runner.run(
            stop_argv,
            elevated=elevated,
            timeout=timeout_seconds,
        )

        if stop_result.exit_code != 0:
            err_msg_lines = [
                "Twingate connector service 'stop' command failed.",
                f"ARGV: {stop_argv}",
                f"EXIT_CODE: {stop_result.exit_code}",
                "STDERR:",
                stop_result.stderr if stop_result.stderr is not None else "",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNBringDownError(
                err_msg,
                exit_code=stop_result.exit_code,
                stderr=stop_result.stderr,
            )

        return None

    def status(self, *,
               aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> VPNStatus:
        """
            Query the local connector service for its current state.

            Reads are never elevated regardless of the ``elevated`` aspect —
            ``systemctl is-active`` does not require root.

            :param aspects: Behaviour control for the call.

            :returns: A :class:`VPNStatus` snapshot. ``self_address`` is
                always ``None`` for Twingate connectors.
        """

        if aspects.dry_run:
            rtnval = VPNStatus(
                connected=False,
                backend_state="dry-run",
                self_address=None,
                hostname=None,
                tags=[],
                provider=PROVIDER_NAME,
            )
            self._last_status = rtnval
            return rtnval

        status_argv = compose_service_argv(action="is-active")

        timeout_seconds = aspects.command_timeout_seconds

        status_result: RunResult = self._command_runner.run(
            status_argv,
            elevated=False,
            timeout=timeout_seconds,
        )

        stdout_text = status_result.stdout
        if stdout_text is None:
            stdout_text = ""

        backend_state = stdout_text.strip()
        connected = False
        if backend_state == "active":
            connected = True

        rtnval = VPNStatus(
            connected=connected,
            backend_state=backend_state,
            self_address=None,
            hostname=None,
            tags=[],
            provider=PROVIDER_NAME,
        )
        self._last_status = rtnval
        return rtnval

    def self_address(self) -> Optional[str]:
        """
            Return ``None`` unconditionally — Twingate connector hosts are
            not assigned an overlay IP. See class docstring for the design
            rationale.

            :returns: ``None``.
        """
        rtnval = None
        return rtnval

    def peer_addresses(self) -> Dict[str, str]:
        """
            Return an empty mapping unconditionally.

            Twingate is resource-scoped rather than flat-mesh; peer
            enumeration belongs to the control plane, not the local daemon.
            A single DEBUG message is emitted per process the first time
            this method is called.

            :returns: An empty ``Dict[str, str]``.
        """
        global _PEER_ENUMERATION_WARNING_EMITTED
        if not _PEER_ENUMERATION_WARNING_EMITTED:
            self._logger.debug(
                "Twingate does not expose peer enumeration on the local connector; "
                "peer_addresses() returns an empty mapping by design. "
                "See vpn-twingate-client design.md for the rationale."
            )
            _PEER_ENUMERATION_WARNING_EMITTED = True

        rtnval = {}
        return rtnval


__all__ = ["TwingateClient", "PROVIDER_NAME"]
