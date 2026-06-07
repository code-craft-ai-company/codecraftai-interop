"""
    .. module:: accessgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`AccessGroup` helper that
                   wraps the Twingate ``resourceAccessAdd`` / ``Remove``
                   mutation surface.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os

from typing import Dict

from ccai.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)
from ccai.interop.vpn.twingate.exceptions import VPNControlPlaneACLError


RESOURCE_ACCESS_ADD_MUTATION = (
    "mutation ResourceAccessAdd($resourceId: ID!, $principalId: ID!) {"
    " resourceAccessAdd(resourceId: $resourceId, principalId: $principalId) {"
    " ok error } }"
)

RESOURCE_ACCESS_REMOVE_MUTATION = (
    "mutation ResourceAccessRemove($resourceId: ID!, $principalId: ID!) {"
    " resourceAccessRemove(resourceId: $resourceId, principalId: $principalId) {"
    " ok error } }"
)


class AccessGroup:
    """
        Helper that wraps the Twingate ``resourceAccess*`` mutation surface.
    """

    def __init__(self, *, client: "object"):
        """
            Initialize the access group.

            :param client: The parent :class:`TwingateControlPlane`.

            :returns: ``None``.
        """
        self._client = client
        return

    def add(self, *, group_id: str, resource_id: str,
            aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> None:
        """
            Issue a ``resourceAccessAdd`` mutation binding ``group_id`` to
            ``resource_id``.

            :param group_id: Provider-assigned group identifier.
            :param resource_id: Provider-assigned resource identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": RESOURCE_ACCESS_ADD_MUTATION,
            "variables": {
                "resourceId": resource_id,
                "principalId": group_id,
            },
            "operationName": "ResourceAccessAdd",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        _raise_if_access_mutation_failed(
            payload=payload, mutation_name="resourceAccessAdd"
        )
        return None

    def remove(self, *, group_id: str, resource_id: str,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> None:
        """
            Issue a ``resourceAccessRemove`` mutation removing the binding
            from ``group_id`` to ``resource_id``.

            :param group_id: Provider-assigned group identifier.
            :param resource_id: Provider-assigned resource identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": RESOURCE_ACCESS_REMOVE_MUTATION,
            "variables": {
                "resourceId": resource_id,
                "principalId": group_id,
            },
            "operationName": "ResourceAccessRemove",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        _raise_if_access_mutation_failed(
            payload=payload, mutation_name="resourceAccessRemove"
        )
        return None


def _raise_if_access_mutation_failed(*, payload: Dict, mutation_name: str) -> None:
    """
        Raise :class:`VPNControlPlaneACLError` when ``payload`` reports the
        access mutation did not succeed.

        :param payload: Decoded GraphQL response.
        :param mutation_name: Mutation field name to read from ``data``.

        :returns: ``None``.
    """
    errors = payload.get("errors")
    if errors is not None and len(errors) > 0:
        err_msg_lines = [
            f"Twingate {mutation_name} returned top-level GraphQL errors.",
            f"ERRORS: {errors}",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise VPNControlPlaneACLError(
            err_msg,
            response_body=str(payload),
        )

    data = payload.get("data")
    if data is None:
        err_msg_lines = [
            f"Twingate {mutation_name} returned no 'data' payload.",
            f"PAYLOAD: {payload}",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise VPNControlPlaneACLError(
            err_msg,
            response_body=str(payload),
        )

    result = data.get(mutation_name)
    if result is None or result.get("ok") is not True:
        err_msg_lines = [
            f"Twingate {mutation_name} did not succeed.",
            f"RESULT: {result}",
        ]
        err_msg = os.linesep.join(err_msg_lines)
        raise VPNControlPlaneACLError(
            err_msg,
            response_body=str(payload),
        )

    return None


__all__ = [
    "AccessGroup",
    "RESOURCE_ACCESS_ADD_MUTATION",
    "RESOURCE_ACCESS_REMOVE_MUTATION",
]
