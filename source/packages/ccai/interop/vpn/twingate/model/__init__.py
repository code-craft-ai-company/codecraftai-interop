"""
    .. module:: model
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Subpackage containing the Twingate GraphQL data model
                   dataclasses (connectors, resources, groups).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.interop.vpn.twingate.model.twingateconnector import TwingateConnector
from ccai.interop.vpn.twingate.model.twingateresource import TwingateResource
from ccai.interop.vpn.twingate.model.twingategroup import TwingateGroup


__all__ = ["TwingateConnector", "TwingateResource", "TwingateGroup"]
