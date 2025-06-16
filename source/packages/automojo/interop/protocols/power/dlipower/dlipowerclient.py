

"""
    .. module:: dlipowerclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dlipowerclient module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Optional


from automojo.credentials.basiccredential import BasicCredential


from automojo.interop.protocols.rest.aspectsrest import AspectsRest, DEFAULT_REST_ASPECTS
from automojo.interop.protocols.rest.restclientbase import RestClientBase

from automojo.interop.protocols.power.dlipower.restapis.apinoderelay import ApiNodeRelay


class DliPowerRestClient(RestClientBase):
    """
        REST client for interacting with Digital Loggers power controllers.
    """

    def __init__(self, host: str, credential: BasicCredential, port: Optional[int] = None,
                 scheme: Optional[str] = "https", aspects: AspectsRest = DEFAULT_REST_ASPECTS) -> None:
        """
            Initializes a :class:`DliPowerRestClient` instance.

            :param host: Hostname or IP address of the power controller.
            :param credential: Credentials used for authentication.
            :param port: Optional TCP port for the REST service.
            :param scheme: HTTP scheme used to communicate with the service.
            :param aspects: Default REST aspects used when making calls.
        """
        super().__init__(host, credential, port, scheme, aspects)

        self._node_relay = ApiNodeRelay(self)

        return
    
    @property
    def relay(self) -> ApiNodeRelay:
        """
            Provides access to the node relay REST interface.

            :returns: An :class:`ApiNodeRelay` instance for this client.
        """
        return self._node_relay



if __name__ == "__main__":
    credobj = BasicCredential(identifier="admin", categories=["rest"], username="admin", password="Acess2Power!!")

    client = DliPowerRestClient("172.16.1.150", credobj)

    client.relay.get_outlets()

