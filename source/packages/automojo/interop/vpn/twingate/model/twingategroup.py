"""
    .. module:: twingategroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TwingateGroup` data class
                   representing a group entity from the Twingate GraphQL API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass, field
from typing import List


@dataclass
class TwingateGroup:
    """
        Typed projection of a Twingate ``Group`` node.

        :param group_id: Provider-assigned stable identifier.
        :param name: Display name of the group.
        :param user_ids: Identifiers of users in the group.
    """
    group_id: str
    name: str
    user_ids: List[str] = field(default_factory=list)


__all__ = ["TwingateGroup"]
