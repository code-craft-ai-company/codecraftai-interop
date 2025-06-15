

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


from automojo.interop.protocols.rest.aspectsrest import AspectsRest


from automojo.interop.protocols.power.dlipower.responsemodel import Outlet

if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient


class ApiNodeRelay:
    """
        Interface layer for REST operations on power relay nodes.
    """

    def __init__(self, client: "DliPowerRestClient") -> None:
        """
            Initializes an :class:`ApiNodeRelay` instance.

            :param client: Client used to issue REST requests.
        """
        self._client_ref = weakref.ref(client)
        return
    
    def client(self) -> "DliPowerRestClient":
        """
            Returns the associated :class:`DliPowerRestClient` instance.
        """
        return self._client_ref()
    

    def get_outlets(self, aspects: Optional[AspectsRest] = None) -> List[Outlet]:
        """
            Retrieves outlet details from the power controller.
        """

        leaf = "restapi/relay/outlets"

        client: "DliPowerRestClient" = self.client

        rtnval = None

        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        rtnval = resp.json()

        return rtnval
