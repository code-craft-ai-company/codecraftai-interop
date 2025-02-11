

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Optional


from automojo.credentials.basiccredential import BasicCredential


from automojo.interop.protocols.rest.aspectsrest import AspectsRest, DEFAULT_REST_ASPECTS
from automojo.interop.protocols.rest.restclientbase import RestClientBase

from automojo.interop.protocols.power.dlipower.restapis.apinoderelay import ApiNodeRelay


class DliPowerRestClient(RestClientBase):

    def __init__(self, host: str, credential: BasicCredential, port: Optional[int] = None, scheme: Optional[str] = "https", aspects: AspectsRest = DEFAULT_REST_ASPECTS):
        super().__init__(host, credential, port, scheme, aspects)

        self._node_relay = ApiNodeRelay(self)

        return
    
    @property
    def relay(self) -> ApiNodeRelay:
        return self._node_relay



if __name__ == "__main__":
    credobj = BasicCredential(identifier="admin", categories=["rest"], username="admin", password="Acess2Power!!")

    client = DliPowerRestClient("172.16.1.150", credobj)

    client.relay.get_outlets()