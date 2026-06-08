"""
    .. module:: statusparser
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`StatusParser` helper used
                   to map ``tailscale status --json`` payloads into typed
                   :class:`VPNStatus` snapshots and peer mappings.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import ipaddress
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from ccai.interfaces.ivpnclient import VPNStatus

from ccai.interop.vpn.tailscale.exceptions import VPNStatusError


CGNAT_NETWORK = ipaddress.ip_network("100.64.0.0/10")

PROVIDER_TAILSCALE = "tailscale"


class StatusParser:
    """
        :class:`StatusParser` is a stateless helper class that converts
        ``tailscale status --json`` output (or a ``Logged out`` stderr signal)
        into :class:`VPNStatus` instances and into peer-name -> overlay-IP
        mappings.

        The class is intentionally constructed without state so the same
        instance can be reused across calls and across threads.
    """

    def __init__(self):
        """
            Initialize the parser. No state is stored.

            :returns: ``None``.
        """
        return

    def parse_status(self, *, stdout: str, stderr: str, exit_code: int) -> VPNStatus:
        """
            Convert a ``tailscale status --json`` invocation result into a
            :class:`VPNStatus`.

            :param stdout: The raw stdout text from the command runner.
            :param stderr: The raw stderr text from the command runner.
            :param exit_code: The exit code reported by the command runner.

            :returns: A :class:`VPNStatus` snapshot.

            :raises: :class:`VPNStatusError` when the stdout body is non-empty
                and cannot be parsed as JSON.
        """
        if exit_code != 0:
            logged_out_status = self._maybe_logged_out(stderr=stderr, stdout=stdout)
            if logged_out_status is not None:
                rtnval = logged_out_status
                return rtnval

            err_msg_lines = ["Failed to parse tailscale status — non-zero exit."]
            err_msg_lines.append("EXIT_CODE: {}".format(exit_code))
            err_msg_lines.append("STDERR:")
            err_msg_lines.append(stderr)
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNStatusError(err_msg, raw_stdout=stdout)

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as jerr:
            err_msg_lines = ["Failed to decode tailscale status JSON body."]
            err_msg_lines.append("ERROR: {}".format(jerr))
            err_msg_lines.append("STDOUT:")
            err_msg_lines.append(stdout)
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNStatusError(err_msg, raw_stdout=stdout) from jerr

        rtnval = self._payload_to_status(payload=payload)
        return rtnval

    def parse_peers(self, *, stdout: str) -> Dict[str, str]:
        """
            Convert a ``tailscale status --json`` payload into a mapping from
            peer short hostname to overlay IPv4 address selected from the
            CGNAT range.

            :param stdout: The raw stdout text from the command runner.

            :returns: A mapping of peer short hostname to overlay address.

            :raises: :class:`VPNStatusError` when the body cannot be parsed.
        """
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as jerr:
            err_msg_lines = ["Failed to decode tailscale status JSON body for peers."]
            err_msg_lines.append("ERROR: {}".format(jerr))
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNStatusError(err_msg, raw_stdout=stdout) from jerr

        peers_map = payload.get("Peer")
        if peers_map is None:
            rtnval: Dict[str, str] = {}
            return rtnval

        rtnval = {}
        for peer_key, peer_entry in peers_map.items():
            host_short, overlay_ip = self._extract_peer(peer_entry=peer_entry)
            if host_short is None:
                continue
            if overlay_ip is None:
                continue
            rtnval[host_short] = overlay_ip

        return rtnval

    def _payload_to_status(self, *, payload: Dict[str, Any]) -> VPNStatus:
        """
            Translate a parsed ``tailscale status --json`` dictionary into a
            :class:`VPNStatus`.

            :param payload: The decoded JSON payload.

            :returns: A :class:`VPNStatus` snapshot.
        """
        backend_state = payload.get("BackendState")
        if backend_state is None:
            backend_state = ""

        connected = backend_state == "Running"

        self_entry = payload.get("Self")
        if self_entry is None:
            self_entry = {}

        self_address = self._first_cgnat(addresses=self_entry.get("TailscaleIPs"))
        hostname = self_entry.get("HostName")
        raw_tags = self_entry.get("Tags")
        tags: List[str] = []
        if raw_tags is not None:
            for tag_value in raw_tags:
                tags.append(tag_value)

        rtnval = VPNStatus(connected=connected,
                           backend_state=backend_state,
                           self_address=self_address,
                           hostname=hostname,
                           tags=tags,
                           provider=PROVIDER_TAILSCALE)
        return rtnval

    def _extract_peer(self, *, peer_entry: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """
            Extract the short hostname and overlay CGNAT address from a peer
            entry dictionary.

            :param peer_entry: A single peer entry from the ``Peer`` map.

            :returns: A tuple of ``(short_host, overlay_ip)``; either side
                MAY be ``None`` when the entry omits the corresponding field.
        """
        host_short = peer_entry.get("HostName")
        overlay_ip = self._first_cgnat(addresses=peer_entry.get("TailscaleIPs"))
        rtnval = (host_short, overlay_ip)
        return rtnval

    def _first_cgnat(self, *, addresses: Optional[List[str]]) -> Optional[str]:
        """
            Select the first address that belongs to the Tailscale CGNAT
            ``100.64.0.0/10`` overlay range.

            :param addresses: A list of address strings, or ``None``.

            :returns: The first CGNAT address, or ``None`` when none match.
        """
        if addresses is None:
            rtnval: Optional[str] = None
            return rtnval
        if len(addresses) == 0:
            rtnval = None
            return rtnval

        for addr_str in addresses:
            try:
                addr_obj = ipaddress.ip_address(addr_str)
            except ValueError:
                continue
            if addr_obj.version != 4:
                continue
            if addr_obj in CGNAT_NETWORK:
                rtnval = addr_str
                return rtnval

        rtnval = None
        return rtnval

    def _maybe_logged_out(self, *, stderr: str, stdout: str) -> Optional[VPNStatus]:
        """
            Detect the ``Logged out`` non-zero case and return an empty
            :class:`VPNStatus` when found.

            :param stderr: The stderr text from the command runner.
            :param stdout: The stdout text from the command runner.

            :returns: A non-connected :class:`VPNStatus` when the signal is
                detected, or ``None`` otherwise.
        """
        combined = (stderr or "") + (stdout or "")
        if "Logged out" not in combined:
            rtnval: Optional[VPNStatus] = None
            return rtnval

        rtnval = VPNStatus(connected=False,
                           backend_state="Stopped",
                           self_address=None,
                           hostname=None,
                           tags=[],
                           provider=PROVIDER_TAILSCALE)
        return rtnval
