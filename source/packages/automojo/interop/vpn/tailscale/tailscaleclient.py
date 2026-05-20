"""
    .. module:: tailscaleclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TailscaleClient` host-side
                   client which drives the local ``tailscale`` CLI through an
                   injected :class:`ICommandRunner`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import os
from typing import Dict, List, Optional

from automojo.interfaces.icommandrunner import ICommandRunner, RunResult
from automojo.interfaces.ifileoperator import IFileOperator
from automojo.interfaces.ivpnclient import VPNStatus

from automojo.interop.vpn.aspectsvpnclient import (
    AspectsVPNClient, DEFAULT_VPN_CLIENT_ASPECTS
)
from automojo.interop.vpn.tailscale.exceptions import (
    VPNBringDownError, VPNBringUpError
)
from automojo.interop.vpn.tailscale.statusparser import (
    StatusParser, PROVIDER_TAILSCALE
)


TAILSCALE_BINARY = "tailscale"


class TailscaleClient:
    """
        :class:`TailscaleClient` is the canonical host-side client for a
        Tailscale-joined node. It implements the
        :class:`automojo.interfaces.ivpnclient.IVPNClient` protocol and drives
        the local ``tailscale`` CLI through an injected
        :class:`ICommandRunner`.

        The class never talks to ``api.tailscale.com`` directly; that surface
        belongs to :class:`TailscaleControlPlane`. Behaviour-modifying
        parameters ride on :class:`AspectsVPNClient`; no decorator-based
        retries or timeouts are used.
    """

    def __init__(self, *, command_runner: ICommandRunner,
                 file_operator: Optional[IFileOperator] = None,
                 aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS):
        """
            Initialize a Tailscale client bound to an injected command runner.

            :param command_runner: Command runner used to invoke
                ``tailscale`` subcommands. The runner can be a local runner or
                an SSH runner with no code differences.
            :param file_operator: Optional file operator. Not required for
                Tailscale today; reserved for future state-file workflows.
            :param aspects: Default aspects applied when a call omits an
                explicit ``aspects`` argument.

            :returns: ``None``.
        """
        self._command_runner = command_runner
        self._file_operator = file_operator
        self._aspects = aspects
        self._parser = StatusParser()
        self._last_status: Optional[VPNStatus] = None
        return

    @property
    def aspects(self) -> AspectsVPNClient:
        """
            Default aspects for this client.

            :returns: The :class:`AspectsVPNClient` instance supplied at
                construction time.
        """
        rtnval = self._aspects
        return rtnval

    def bring_up(self, *, authkey: str, hostname: Optional[str] = None,
                 advertise_tags: Optional[List[str]] = None,
                 aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> VPNStatus:
        """
            Bring the local ``tailscaled`` daemon up and join the tailnet.

            :param authkey: A Tailscale auth key. Must be non-empty.
            :param hostname: Hostname to register with the control plane, or
                ``None`` to defer to the daemon default.
            :param advertise_tags: Tags to advertise, or ``None``/empty to
                omit the flag.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`VPNStatus` reflecting the post-bring-up state.

            :raises: :class:`VPNBringUpError` when ``tailscale up`` exits
                non-zero.
        """
        if authkey is None:
            raise ValueError("'authkey' must be a non-empty string.")
        if len(authkey) == 0:
            raise ValueError("'authkey' must be a non-empty string.")

        if aspects.dry_run:
            rtnval = self._dry_run_status()
            self._last_status = rtnval
            return rtnval

        argv = self._compose_up_argv(authkey=authkey,
                                     hostname=hostname,
                                     advertise_tags=advertise_tags)

        run_result = self._command_runner.run(argv,
                                              elevated=aspects.elevated,
                                              timeout=aspects.command_timeout_seconds)

        if run_result.exit_code != 0:
            err_msg_lines = ["'tailscale up' returned a non-zero exit code."]
            err_msg_lines.append("EXIT_CODE: {}".format(run_result.exit_code))
            err_msg_lines.append("STDERR:")
            err_msg_lines.append(run_result.stderr)
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNBringUpError(err_msg,
                                  exit_code=run_result.exit_code,
                                  stderr=run_result.stderr)

        rtnval = self.status(aspects=aspects)
        return rtnval

    def bring_down(self, *, aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> None:
        """
            Bring the local ``tailscaled`` daemon down.

            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`VPNBringDownError` when ``tailscale down`` exits
                non-zero.
        """
        if aspects.dry_run:
            return

        argv = [TAILSCALE_BINARY, "down"]
        run_result = self._command_runner.run(argv,
                                              elevated=aspects.elevated,
                                              timeout=aspects.command_timeout_seconds)

        if run_result.exit_code != 0:
            err_msg_lines = ["'tailscale down' returned a non-zero exit code."]
            err_msg_lines.append("EXIT_CODE: {}".format(run_result.exit_code))
            err_msg_lines.append("STDERR:")
            err_msg_lines.append(run_result.stderr)
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNBringDownError(err_msg,
                                    exit_code=run_result.exit_code,
                                    stderr=run_result.stderr)

        self._last_status = None
        return

    def status(self, *, aspects: AspectsVPNClient = DEFAULT_VPN_CLIENT_ASPECTS) -> VPNStatus:
        """
            Query the local daemon for its current status.

            :param aspects: Behaviour control for the call.

            :returns: A :class:`VPNStatus` snapshot.

            :raises: :class:`VPNStatusError` when the JSON body cannot be
                parsed.
        """
        if aspects.dry_run:
            rtnval = self._dry_run_status()
            self._last_status = rtnval
            return rtnval

        argv = [TAILSCALE_BINARY, "status", "--json"]
        run_result: RunResult = self._command_runner.run(argv,
                                                         elevated=False,
                                                         timeout=aspects.command_timeout_seconds)

        rtnval = self._parser.parse_status(stdout=run_result.stdout,
                                           stderr=run_result.stderr,
                                           exit_code=run_result.exit_code)
        self._last_status = rtnval
        return rtnval

    def self_address(self) -> Optional[str]:
        """
            Return the local overlay address, refreshing the cached status
            with default aspects when no cached snapshot is present.

            :returns: An overlay address string, or ``None`` when none is
                assigned.
        """
        if self._last_status is None:
            self.status(aspects=self._aspects)

        if self._last_status is None:
            rtnval: Optional[str] = None
            return rtnval

        rtnval = self._last_status.self_address
        return rtnval

    def peer_addresses(self) -> Dict[str, str]:
        """
            Return a mapping of peer short hostname to overlay IP from the
            latest ``tailscale status --json`` payload.

            :returns: A mapping of peer hostname to overlay IP. An empty dict
                is returned when no peers are present.
        """
        argv = [TAILSCALE_BINARY, "status", "--json"]
        run_result: RunResult = self._command_runner.run(argv,
                                                         elevated=False,
                                                         timeout=self._aspects.command_timeout_seconds)

        if run_result.exit_code != 0:
            rtnval: Dict[str, str] = {}
            return rtnval

        rtnval = self._parser.parse_peers(stdout=run_result.stdout)
        return rtnval

    def _compose_up_argv(self, *, authkey: str, hostname: Optional[str],
                         advertise_tags: Optional[List[str]]) -> List[str]:
        """
            Compose the ``tailscale up`` argv list for the supplied flag set.

            :param authkey: The auth key to embed in the ``--authkey`` flag.
            :param hostname: Optional hostname flag value.
            :param advertise_tags: Optional advertise-tag list.

            :returns: The fully composed argv list ready for the command
                runner.
        """
        argv: List[str] = [TAILSCALE_BINARY, "up", "--authkey={}".format(authkey)]

        if hostname is not None:
            argv.append("--hostname={}".format(hostname))

        if advertise_tags is not None and len(advertise_tags) > 0:
            tag_csv = ",".join(advertise_tags)
            argv.append("--advertise-tags={}".format(tag_csv))

        return argv

    def _dry_run_status(self) -> VPNStatus:
        """
            Build the sentinel :class:`VPNStatus` returned for dry-run calls.

            :returns: A :class:`VPNStatus` with ``connected=False`` and the
                backend state set to the ``dry-run`` sentinel.
        """
        rtnval = VPNStatus(connected=False,
                           backend_state="dry-run",
                           self_address=None,
                           hostname=None,
                           tags=[],
                           provider=PROVIDER_TAILSCALE)
        return rtnval
