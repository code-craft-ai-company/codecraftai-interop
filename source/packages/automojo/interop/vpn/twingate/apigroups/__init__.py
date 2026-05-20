"""
    .. module:: apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Subpackage containing the Twingate GraphQL API group helper
                   classes used by :class:`TwingateControlPlane`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vpn.twingate.apigroups.connectorsgroup import ConnectorsGroup
from automojo.interop.vpn.twingate.apigroups.resourcesgroup import ResourcesGroup
from automojo.interop.vpn.twingate.apigroups.groupsgroup import GroupsGroup
from automojo.interop.vpn.twingate.apigroups.accessgroup import AccessGroup


__all__ = ["ConnectorsGroup", "ResourcesGroup", "GroupsGroup", "AccessGroup"]
