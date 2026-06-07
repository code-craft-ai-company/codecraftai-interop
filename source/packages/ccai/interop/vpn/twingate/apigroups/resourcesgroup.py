"""
    .. module:: resourcesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ResourcesGroup` helper
                   wrapping the Twingate GraphQL resource-management surface.

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
from ccai.interop.vpn.twingate.model.twingateresource import TwingateResource


LIST_RESOURCES_QUERY = (
    "query ListResources {"
    " resources { edges { node { id name address { value } } } }"
    " }"
)

RESOURCE_CREATE_MUTATION = (
    "mutation ResourceCreate($name: String!, $address: String!, $remoteNetworkId: ID!) {"
    " resourceCreate(name: $name, address: $address, remoteNetworkId: $remoteNetworkId) {"
    " ok error entity { id name } } }"
)

RESOURCE_UPDATE_MUTATION = (
    "mutation ResourceUpdate($id: ID!, $name: String, $address: String) {"
    " resourceUpdate(id: $id, name: $name, address: $address) {"
    " ok error entity { id name } } }"
)


class ResourcesGroup:
    """
        Helper that wraps the Twingate ``resources`` GraphQL surface.
    """

    def __init__(self, *, client: "object"):
        """
            Initialize the resources group.

            :param client: The parent :class:`TwingateControlPlane`.

            :returns: ``None``.
        """
        self._client = client
        return

    def list(self, *,
             aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> List[TwingateResource]:
        """
            List resources.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`TwingateResource` records.

            :raises: :class:`VPNControlPlaneQueryError`.
        """
        body = {
            "query": LIST_RESOURCES_QUERY,
            "operationName": "ListResources",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)

        errors = payload.get("errors")
        if errors is not None and len(errors) > 0:
            err_msg_lines = [
                "Twingate 'resources' query returned top-level GraphQL errors.",
                f"ERRORS: {errors}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneQueryError(
                err_msg,
                response_body=str(payload),
            )

        data = payload.get("data")
        if data is None:
            rtnval: List[TwingateResource] = []
            return rtnval

        resources_block = data.get("resources")
        if resources_block is None:
            rtnval = []
            return rtnval

        edges = resources_block.get("edges")
        if edges is None:
            edges = []

        results: List[TwingateResource] = []
        for edge in edges:
            node = edge.get("node")
            if node is None:
                continue
            resource_id = node.get("id", "")
            name = node.get("name", "")
            address_block = node.get("address")
            address = ""
            if address_block is not None:
                address = address_block.get("value", "")
            record = TwingateResource(
                resource_id=resource_id,
                name=name,
                address=address,
                protocols={},
            )
            results.append(record)

        rtnval = results
        return rtnval

    def create(self, *, name: str, address: str, remote_network_id: str,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> TwingateResource:
        """
            Create a resource.

            :param name: Resource display name.
            :param address: FQDN, IP, or CIDR.
            :param remote_network_id: Parent remote-network identifier.
            :param aspects: Behaviour control for the call.

            :returns: The newly created :class:`TwingateResource`.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": RESOURCE_CREATE_MUTATION,
            "variables": {
                "name": name,
                "address": address,
                "remoteNetworkId": remote_network_id,
            },
            "operationName": "ResourceCreate",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        rtnval = self._parse_resource_mutation(
            payload=payload, mutation_name="resourceCreate", body=body
        )
        return rtnval

    def update(self, *, resource_id: str, name: Optional[str] = None,
               address: Optional[str] = None,
               aspects: AspectsTwingate = DEFAULT_TWINGATE_ASPECTS) -> TwingateResource:
        """
            Update a resource.

            :param resource_id: Provider-assigned identifier.
            :param name: New display name, or ``None`` to leave unchanged.
            :param address: New address, or ``None`` to leave unchanged.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`TwingateResource`.

            :raises: :class:`VPNControlPlaneACLError`.
        """
        body = {
            "query": RESOURCE_UPDATE_MUTATION,
            "variables": {
                "id": resource_id,
                "name": name,
                "address": address,
            },
            "operationName": "ResourceUpdate",
        }

        payload = self._client.graphql_call(body=body, aspects=aspects)
        rtnval = self._parse_resource_mutation(
            payload=payload, mutation_name="resourceUpdate", body=body
        )
        return rtnval

    def _parse_resource_mutation(self, *, payload: Dict, mutation_name: str,
                                 body: Dict) -> TwingateResource:
        """
            Parse a resource mutation payload into a :class:`TwingateResource`.

            :param payload: Decoded GraphQL response.
            :param mutation_name: Mutation field name to read from ``data``.
            :param body: Original request body, for error context.

            :returns: The :class:`TwingateResource` projection.

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
        if result is None:
            err_msg_lines = [
                f"Twingate {mutation_name} returned no result object.",
                f"PAYLOAD: {payload}",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise VPNControlPlaneACLError(
                err_msg,
                response_body=str(payload),
            )

        if result.get("ok") is not True:
            err_msg_lines = [
                f"Twingate {mutation_name} reported ok=False.",
                f"ERROR: {result.get('error')}",
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

        rtnval = TwingateResource(
            resource_id=entity.get("id", ""),
            name=entity.get("name", ""),
            address=body.get("variables", {}).get("address", "") or "",
            protocols={},
        )
        return rtnval


__all__ = [
    "ResourcesGroup",
    "LIST_RESOURCES_QUERY",
    "RESOURCE_CREATE_MUTATION",
    "RESOURCE_UPDATE_MUTATION",
]
