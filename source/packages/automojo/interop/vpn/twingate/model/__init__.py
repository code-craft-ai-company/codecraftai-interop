"""
    .. module:: model
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Subpackage containing the Twingate GraphQL data model
                   dataclasses (connectors, resources, groups).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.vpn.twingate.model.twingateconnector import TwingateConnector
from automojo.interop.vpn.twingate.model.twingateresource import TwingateResource
from automojo.interop.vpn.twingate.model.twingategroup import TwingateGroup


__all__ = ["TwingateConnector", "TwingateResource", "TwingateGroup"]
