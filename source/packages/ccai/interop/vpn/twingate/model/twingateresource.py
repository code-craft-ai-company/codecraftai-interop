"""
    .. module:: twingateresource
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TwingateResource` data
                   class representing a resource entity from the Twingate
                   GraphQL API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TwingateResource:
    """
        Typed projection of a Twingate ``Resource`` node.

        :param resource_id: Provider-assigned stable identifier.
        :param name: Display name of the resource.
        :param address: Address shape — FQDN, IP, or CIDR.
        :param protocols: Allowed protocol map keyed by protocol name
            (``tcp``, ``udp``) holding the list of port numbers.
    """
    resource_id: str
    name: str
    address: str
    protocols: Dict[str, List[int]] = field(default_factory=dict)


__all__ = ["TwingateResource"]
