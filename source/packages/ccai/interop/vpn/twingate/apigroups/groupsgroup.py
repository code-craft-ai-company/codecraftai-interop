"""
    .. module:: groupsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`GroupsGroup` helper
                   wrapping the Twingate GraphQL group-management surface.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os

from typing import Dict, List, Optional

from ccai.interop.vpn.twingate.aspectstwingate import (
    AspectsTwingate, DEFAULT_TWINGATE_ASPECTS
)
from ccai.interop.vpn.twingate.exceptions import (
    VPNControlPlaneACLError, VPNControlPlaneQueryError,
)
from ccai.interop.vpn.twingate.model.twingategroup import TwingateGroup


LIST_GROUPS_QUERY = (
    "query ListGroups {"
    " groups { edges { node { id name } } }"
    " }"
)

GROUP_CREATE_MUTATION = (
    "mutation GroupCreate($name: String!) {"
    " groupCreate(name: $name) { ok error entity { id name } } }"
)

GROUP_UPDATE_MUTATION = (
    "mutation GroupUpdate($id: ID!, $name: String) {"
    " groupUpdate(id: $id, name: $name) { ok error entity { id name } } }"
)


class GroupsGroup:
    """
        Helper that wraps the Twingate ``groups`` GraphQL surface.
    """

    def __init__(self, *, client: "object"):
        """
            Initialize the groups group.

            :param client: The parent :class:`TwingateControlPlane`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *,
             aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> List[TwingateGroup]:
        """
            List groups.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`TwingateGroup` records.

            :raises: :class:`VPNControlPlaneQueryError`.
        """
        body = {
            "query": LIST_GROUPS_QUERY,
            "operationName": "ListGroups",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)

        errors = payload.get("errors")
        if errors is not None and len(errors) > 0:
            err_msg_lines = [
                "Twingate 'groups' query returned top-level GraphQL errors.",
                f"ERRORS: {errors}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneQueryError(
                err_msg,
                response_body=str(payload),
            )

        data = payload.get("data")
        if data is None:
            rtnval: List[TwingateGroup] = []
            return rtnval

        groups_block = data.get("groups")
        if groups_block is None:
            rtnval = []
            return rtnval

        edges = groups_block.get("edges")
        if edges is None:
            edges = []

        results: List[TwingateGroup] = []
        for edge in edges:
            node = edge.get("node")
            if node is None:
                continue
            record = TwingateGroup(
                group_id=node.get("id", ""),
                name=node.get("name", ""),
                user_ids=[],
            )
            results.append(record)

        rtnval = results
        return rtnval

    def create(self, *, name: str,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> TwingateGroup:
        """
            Create a group.

            :param name: Group display name.
            :param aspects: Behaviour control for the call.

            :returns: The newly created :class:`TwingateGroup`.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": GROUP_CREATE_MUTATION,
            "variables": {"name": name},
            "operationName": "GroupCreate",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        rtnval = self._parse_group_mutation(
            payload=payload, mutation_name="groupCreate"
        )
        return rtnval

    def update(self, *, group_id: str, name: Optional[str] = None,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> TwingateGroup:
        """
            Update a group.

            :param group_id: Provider-assigned identifier.
            :param name: New display name, or ``None`` to leave unchanged.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`TwingateGroup`.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": GROUP_UPDATE_MUTATION,
            "variables": {"id": group_id, "name": name},
            "operationName": "GroupUpdate",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        rtnval = self._parse_group_mutation(
            payload=payload, mutation_name="groupUpdate"
        )
        return rtnval

    def _parse_group_mutation(self, *, payload: Dict,
                              mutation_name: str) -> TwingateGroup:
        """
            Parse a group mutation payload into a :class:`TwingateGroup`.

            :param payload: Decoded GraphQL response.
            :param mutation_name: Mutation field name to read from ``data``.

            :returns: The :class:`TwingateGroup` projection.

            :raises: :class:`VPNControlPlaneACLError`.
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

        entity = result.get("entity")
        if entity is None:
            err_msg_lines = [
                f"Twingate {mutation_name} returned ok=True but no entity.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneACLError(
                err_msg,
                response_body=str(payload),
            )

        rtnval = TwingateGroup(
            group_id=entity.get("id", ""),
            name=entity.get("name", ""),
            user_ids=[],
        )
        return rtnval


__all__ = [
    "GroupsGroup",
    "LIST_GROUPS_QUERY",
    "GROUP_CREATE_MUTATION",
    "GROUP_UPDATE_MUTATION",
]
