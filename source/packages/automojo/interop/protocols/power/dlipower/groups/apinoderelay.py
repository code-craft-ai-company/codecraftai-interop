

"""
    .. module:: apinoderelay
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinoderelay module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, TYPE_CHECKING


import weakref

from http import HTTPStatus

import requests


from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup


from automojo.interop.protocols.power.dlipower.responsemodel import Outlet

if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient


class RelayApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on power relay nodes.
    """

    def get_outlets(self, aspects: Optional[AspectsRest] = None) -> List[Outlet]:
        """
            Retrieves outlet details from the power controller.

            :param aspects: Optional REST call aspects configuration.

            :returns: List of :class:`Outlet` objects.
        """

        leaf = "restapi/relay/outlets"

        client: "DliPowerRestClient" = self.client

        rtnval = None

        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        rtnval = resp.json()

        return rtnval
