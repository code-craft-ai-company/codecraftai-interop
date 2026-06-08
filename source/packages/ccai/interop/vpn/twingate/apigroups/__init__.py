"""
    .. module:: apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Subpackage containing the Twingate GraphQL API group helper
                   classes used by :class:`TwingateControlPlane`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.twingate.apigroups.connectorsgroup import ConnectorsGroup
from ccai.interop.vpn.twingate.apigroups.resourcesgroup import ResourcesGroup
from ccai.interop.vpn.twingate.apigroups.groupsgroup import GroupsGroup
from ccai.interop.vpn.twingate.apigroups.accessgroup import AccessGroup


__all__ = ["ConnectorsGroup", "ResourcesGroup", "GroupsGroup", "AccessGroup"]
