

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

from requests import Session

from automojo.credentials.basiccredential import BasicCredential

from automojo.restclient.base.aspectsrest import AspectsRest, DEFAULT_REST_ASPECTS
from automojo.restclient.base.restclientbase import RestClientBase

from automojo.interop.protocols.power.dlipower.groups.apinoderelay import ApiNodeRelay
from automojo.interop.protocols.power.dlipower.groups.apinodeauth import ApiNodeAuth
from automojo.interop.protocols.power.dlipower.groups.apinodeconfig import ApiNodeConfig
from automojo.interop.protocols.power.dlipower.groups.apinodemeter import ApiNodeMeter
from automojo.interop.protocols.power.dlipower.groups.apinodenetwork import ApiNodeNetwork
from automojo.interop.protocols.power.dlipower.groups.apinodeautoping import ApiNodeAutoping
from automojo.interop.protocols.power.dlipower.groups.apinodescript import ApiNodeScript
from automojo.interop.protocols.power.dlipower.groups.apinoderenderer import ApiNodeRenderer


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
        self._node_auth = ApiNodeAuth(self)
        self._node_config = ApiNodeConfig(self)
        self._node_meter = ApiNodeMeter(self)
        self._node_network = ApiNodeNetwork(self)
        self._node_autoping = ApiNodeAutoping(self)
        self._node_script = ApiNodeScript(self)
        self._node_renderer = ApiNodeRenderer(self)


        return

    def authenticate(self):
        """
            Authentication is handled by the requests library using HTTP Digest Authentication.
            We setup the session with the proper authentication handler.
        """
        from requests.auth import HTTPDigestAuth
        
        credential: BasicCredential = self._credential
        
        username = credential.username
        password = credential.password
        
        session = Session()
        session.auth = HTTPDigestAuth(username, password)
        session.verify = self._verify_certificate
        
        self._session = session
        
        return


    @property
    def auth(self) -> ApiNodeAuth:
        """
            Provides access to the node auth REST interface.

            :returns: An :class:`ApiNodeAuth` instance for this client.
        """
        return self._node_auth
    
    @property
    def autoping(self) -> ApiNodeAutoping:
        """
            Provides access to the node autoping REST interface.

            :returns: An :class:`ApiNodeAutoping` instance for this client.
        """
        return self._node_autoping

    @property
    def config(self) -> ApiNodeConfig:
        """
            Provides access to the node config REST interface.

            :returns: An :class:`ApiNodeConfig` instance for this client.
        """
        return self._node_config

    @property
    def meter(self) -> ApiNodeMeter:
        """
            Provides access to the node meter REST interface.

            :returns: An :class:`ApiNodeMeter` instance for this client.
        """
        return self._node_meter

    @property
    def network(self) -> ApiNodeNetwork:
        """
            Provides access to the node network REST interface.

            :returns: An :class:`ApiNodeNetwork` instance for this client.
        """
        return self._node_network

    @property
    def relay(self) -> ApiNodeRelay:
        """
            Provides access to the node relay REST interface.

            :returns: An :class:`ApiNodeRelay` instance for this client.
        """
        return self._node_relay
    
    @property
    def renderer(self) -> ApiNodeRenderer:
        """
            Provides access to the node renderer REST interface.

            :returns: An :class:`ApiNodeRenderer` instance for this client.
        """
        return self._node_renderer

    @property
    def script(self) -> ApiNodeScript:
        """
            Provides access to the node script REST interface.

            :returns: An :class:`ApiNodeScript` instance for this client.
        """
        return self._node_script
    

if __name__ == "__main__":
    credobj = BasicCredential(identifier="admin", categories=["rest"], username="admin", password="Acess2Power!!")

    client = DliPowerRestClient("172.16.1.150", credobj)

    client.relay.get_outlets()

