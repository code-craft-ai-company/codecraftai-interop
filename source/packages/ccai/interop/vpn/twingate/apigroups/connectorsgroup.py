"""
    .. module:: connectorsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ConnectorsGroup` helper
                   that wraps the Twingate GraphQL connector-management
                   surface (``connectorGenerateTokens``, ``connectors`` query,
                   ``connectorDelete``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os

from typing import Any, Dict, List, Optional

from ccai.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)
from ccai.interop.vpn.twingate.exceptions import (
    VPNControlPlaneAuthKeyError,
    VPNControlPlaneQueryError,
    VPNControlPlaneMutationError,
)
from ccai.interop.vpn.twingate.model.twingateconnector import TwingateConnector


GENERATE_TOKENS_MUTATION = (
    "mutation ConnectorGenerateTokens($connectorId: ID!) {"
    " connectorGenerateTokens(connectorId: $connectorId) {"
    " ok error connectorTokens { accessToken refreshToken }"
    " } }"
)

LIST_CONNECTORS_QUERY = (
    "query ListConnectors {"
    " connectors { edges { node {"
    " id name state remoteNetwork { id name }"
    " } } } }"
)

CONNECTOR_DELETE_MUTATION = (
    "mutation ConnectorDelete($id: ID!) {"
    " connectorDelete(id: $id) { ok error }"
    " }"
)


class ConnectorsGroup:
    """
        Helper that issues the GraphQL queries and mutations required to
        manage Twingate connectors. Instances are owned by a
        :class:`TwingateControlPlane` and use that client's
        :meth:`graphql_call` helper to send requests.
    """

    def __init__(self, *, client: "object"):
        """
            Initialize the connectors group.

            :param client: The parent :class:`TwingateControlPlane`.

            :returns: ``None``.
        """
        self._client = client
        return

    def generate_tokens(self, *, connector_id: str,
                        aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> Dict[str, str]:
        """
            Issue the ``connectorGenerateTokens`` mutation against the
            target connector.

            :param connector_id: Provider-assigned connector identifier.
                The caller-provided "tag" identifies the connector by name;
                control-plane code resolves the id before calling this
                helper.
            :param aspects: Behaviour control for the call.

            :returns: A dictionary with ``access_token`` and ``refresh_token``
                keys.

            :raises: :class:`VPNControlPlaneAuthKeyError` when the mutation
                returns a non-ok payload or top-level GraphQL errors.
        """

        if connector_id is None or len(connector_id) == 0:
            err_msg_lines = [
                "ConnectorsGroup.generate_tokens requires a non-empty 'connector_id'.",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(err_msg)

        body = {
            "query": GENERATE_TOKENS_MUTATION,
            "variables": {"connectorId": connector_id},
            "operationName": "ConnectorGenerateTokens",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)

        errors = payload.get("errors")
        if errors is not None and len(errors) > 0:
            err_msg_lines = [
                "Twingate connectorGenerateTokens returned top-level GraphQL errors.",
                f"CONNECTOR_ID: {connector_id}",
                f"ERRORS: {errors}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        data = payload.get("data")
        if data is None:
            err_msg_lines = [
                "Twingate connectorGenerateTokens returned no 'data' payload.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        result = data.get("connectorGenerateTokens")
        if result is None:
            err_msg_lines = [
                "Twingate connectorGenerateTokens returned no result object.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        ok_flag = result.get("ok")
        if ok_flag is not True:
            err_msg_lines = [
                "Twingate connectorGenerateTokens reported ok=False.",
                f"CONNECTOR_ID: {connector_id}",
                f"ERROR: {result.get('error')}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        tokens = result.get("connectorTokens")
        if tokens is None:
            err_msg_lines = [
                "Twingate connectorGenerateTokens returned ok=True but no tokens.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        access_token = tokens.get("accessToken")
        refresh_token = tokens.get("refreshToken")
        if access_token is None or refresh_token is None:
            err_msg_lines = [
                "Twingate connectorGenerateTokens returned an incomplete token pair.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneAuthKeyError(
                err_msg,
                request_body=body,
                response_body=str(payload),
            )

        rtnval = {"access_token": access_token, "refresh_token": refresh_token}
        return rtnval

    def list(self, *,
             aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> List[TwingateConnector]:
        """
            Issue the ``connectors`` query and return the connector list.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`TwingateConnector` records.

            :raises: :class:`VPNControlPlaneQueryError` when the GraphQL
                query returns errors.
        """

        body = {
            "query": LIST_CONNECTORS_QUERY,
            "operationName": "ListConnectors",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)

        errors = payload.get("errors")
        if errors is not None and len(errors) > 0:
            err_msg_lines = [
                "Twingate 'connectors' query returned top-level GraphQL errors.",
                f"ERRORS: {errors}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneQueryError(
                err_msg,
                response_body=str(payload),
            )

        data = payload.get("data")
        if data is None:
            err_msg_lines = [
                "Twingate 'connectors' query returned no 'data' payload.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneQueryError(
                err_msg,
                response_body=str(payload),
            )

        connectors_block = data.get("connectors")
        if connectors_block is None:
            rtnval: List[TwingateConnector] = []
            return rtnval

        edges = connectors_block.get("edges")
        if edges is None:
            edges = []

        results: List[TwingateConnector] = []
        for edge in edges:
            node = edge.get("node")
            if node is None:
                continue
            connector_id = node.get("id", "")
            name = node.get("name", "")
            state = node.get("state", "")
            remote_network = node.get("remoteNetwork")
            remote_network_id = ""
            if remote_network is not None:
                remote_network_id = remote_network.get("id", "")
            record = TwingateConnector(
                connector_id=connector_id,
                name=name,
                remote_network_id=remote_network_id,
                state=state,
            )
            results.append(record)

        rtnval = results
        return rtnval

    def delete(self, *, connector_id: str,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> None:
        """
            Issue the ``connectorDelete`` mutation. Swallows ``not found``
            errors so the call is idempotent.

            :param connector_id: Provider-assigned connector identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`VPNControlPlaneMutationError` when the mutation
                returns any error other than ``not found``.
        """

        if connector_id is None or len(connector_id) == 0:
            err_msg_lines = [
                "ConnectorsGroup.delete requires a non-empty 'connector_id'.",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneMutationError(err_msg)

        body = {
            "query": CONNECTOR_DELETE_MUTATION,
            "variables": {"id": connector_id},
            "operationName": "ConnectorDelete",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)

        errors = payload.get("errors")
        if errors is not None and len(errors) > 0:
            if _errors_indicate_not_found(errors):
                return None
            err_msg_lines = [
                "Twingate connectorDelete returned top-level GraphQL errors.",
                f"CONNECTOR_ID: {connector_id}",
                f"ERRORS: {errors}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneMutationError(
                err_msg,
                response_body=str(payload),
            )

        data = payload.get("data")
        if data is None:
            err_msg_lines = [
                "Twingate connectorDelete returned no 'data' payload.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneMutationError(
                err_msg,
                response_body=str(payload),
            )

        result = data.get("connectorDelete")
        if result is None:
            err_msg_lines = [
                "Twingate connectorDelete returned no result object.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneMutationError(
                err_msg,
                response_body=str(payload),
            )

        ok_flag = result.get("ok")
        if ok_flag is True:
            return None

        error_text = result.get("error")
        if error_text is not None and _is_not_found_error_text(error_text):
            return None

        err_msg_lines = [
            "Twingate connectorDelete reported ok=False.",
            f"CONNECTOR_ID: {connector_id}",
            f"ERROR: {error_text}",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise VPNControlPlaneMutationError(
            err_msg,
            response_body=str(payload),
        )


def _errors_indicate_not_found(errors: List[Dict[str, Any]]) -> bool:
    """
        Inspect the top-level ``errors`` list returned by a GraphQL response
        and return ``True`` when at least one error text suggests the target
        entity does not exist.

        :param errors: The list of error dictionaries.

        :returns: ``True`` when a not-found marker is present.
    """
    indicates_not_found = False
    for entry in errors:
        message = entry.get("message", "")
        if _is_not_found_error_text(message):
            indicates_not_found = True
            break
    return indicates_not_found


def _is_not_found_error_text(text: str) -> bool:
    """
        Return ``True`` when ``text`` indicates a not-found condition.

        :param text: Error text to inspect.

        :returns: ``True`` when the text is recognised as a not-found marker.
    """
    if text is None:
        rtnval = False
        return rtnval
    lowered = text.lower()
    rtnval = False
    if "not found" in lowered:
        rtnval = True
    elif "does not exist" in lowered:
        rtnval = True
    return rtnval


__all__ = [
    "ConnectorsGroup",
    "GENERATE_TOKENS_MUTATION",
    "LIST_CONNECTORS_QUERY",
    "CONNECTOR_DELETE_MUTATION",
]
