

"""
    .. module:: dlipowerclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dlipowerclient module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional

from requests import Session

from ccai.credentials.basiccredential import BasicCredential

from ccai.restclient.base.aspectsrest import AspectsRest, DEFAULT_REST_ASPECTS
from ccai.restclient.base.restclientbase import RestClientBase

from ccai.interop.protocols.power.dlipower.groups.authapigroup import AuthApiGroup
from ccai.interop.protocols.power.dlipower.groups.autopingapigroup import AutopingApiGroup
from ccai.interop.protocols.power.dlipower.groups.configapigroup import ConfigApiGroup
from ccai.interop.protocols.power.dlipower.groups.meterapigroup import MeterApiGroup
from ccai.interop.protocols.power.dlipower.groups.networkapigroup import NetworkApiGroup
from ccai.interop.protocols.power.dlipower.groups.relayapigroup import RelayApiGroup
from ccai.interop.protocols.power.dlipower.groups.rendererapigroup import RendererApiGroup
from ccai.interop.protocols.power.dlipower.groups.scriptapigroup import ScriptApiGroup


class DliPowerRestClient(RestClientBase):
    """
        REST client for interacting with Digital Loggers power controllers.
    """

    def __init__(self, host: str, credential: BasicCredential, port: Optional[int] = None,
                 scheme: Optional[str] = "http", aspects: AspectsRest = DEFAULT_REST_ASPECTS) -> None:
        """
            Initializes a :class:`DliPowerRestClient` instance.

            :param host: Hostname or IP address of the power controller.
            :param credential: Credentials used for authentication.
            :param port: Optional TCP port for the REST service.
            :param scheme: HTTP scheme used to communicate with the service.
            :param aspects: Default REST aspects used when making calls.
        """
        super().__init__(host, credential, port, scheme, aspects)

        self._node_auth = AuthApiGroup(self)
        self._node_autoping = AutopingApiGroup(self)
        self._node_config = ConfigApiGroup(self)
        self._node_meter = MeterApiGroup(self)
        self._node_network = NetworkApiGroup(self)
        self._node_relay = RelayApiGroup(self)
        self._node_renderer = RendererApiGroup(self)
        self._node_script = ScriptApiGroup(self)

        if not self._host_url.endswith("/"):
             self._host_url = f"{self._host_url}/"

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
        session.headers.update({"X-CSRF": "ccai"})
        
        self._session = session
        
        return


    @property
    def auth(self) -> AuthApiGroup:
        """
            Provides access to the node auth REST interface.

            :returns: An :class:`AuthApiGroup` instance for this client.
        """
        return self._node_auth
    
    @property
    def autoping(self) -> AutopingApiGroup:
        """
            Provides access to the node autoping REST interface.

            :returns: An :class:`AutopingApiGroup` instance for this client.
        """
        return self._node_autoping

    @property
    def config(self) -> ConfigApiGroup:
        """
            Provides access to the node config REST interface.

            :returns: An :class:`ConfigApiGroup` instance for this client.
        """
        return self._node_config

    @property
    def meter(self) -> MeterApiGroup:
        """
            Provides access to the node meter REST interface.

            :returns: An :class:`MeterApiGroup` instance for this client.
        """
        return self._node_meter

    @property
    def network(self) -> NetworkApiGroup:
        """
            Provides access to the node network REST interface.

            :returns: An :class:`NetworkApiGroup` instance for this client.
        """
        return self._node_network

    @property
    def relay(self) -> RelayApiGroup:
        """
            Provides access to the node relay REST interface.

            :returns: An :class:`RelayApiGroup` instance for this client.
        """
        return self._node_relay
    
    @property
    def renderer(self) -> RendererApiGroup:
        """
            Provides access to the node renderer REST interface.

            :returns: An :class:`RendererApiGroup` instance for this client.
        """
        return self._node_renderer

    @property
    def script(self) -> ScriptApiGroup:
        """
            Provides access to the node script REST interface.

            :returns: An :class:`ScriptApiGroup` instance for this client.
        """
        return self._node_script
    

if __name__ == "__main__":
    credobj = BasicCredential(identifier="admin", categories=["rest"], username="admin", password="Acess2Power!!")

    client = DliPowerRestClient("172.16.1.150", credobj)

    client.relay.get_outlets()

