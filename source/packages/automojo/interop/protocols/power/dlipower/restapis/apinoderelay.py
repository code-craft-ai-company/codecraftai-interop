

from typing import List, Optional, TYPE_CHECKING


import weakref

from http import HTTPStatus

import requests


from automojo.interop.protocols.rest.aspectsrest import AspectsRest


from automojo.interop.protocols.power.dlipower.responsemodel import Outlet

if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient


class ApiNodeRelay:

    def __init__(self, client: "DliPowerRestClient"):
        self._client_ref = weakref.ref(client)
        return
    
    def client(self) -> "DliPowerRestClient":
        return self._client_ref()
    

    def get_outlets(self, aspects: Optional[AspectsRest] = None) -> List[Outlet]:

        leaf = "restapi/relay/outlets"

        client: "DliPowerRestClient" = self.client

        rtnval = None

        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        rtnval = resp.json()

        return rtnval