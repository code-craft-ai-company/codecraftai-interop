"""
    .. module:: apinodenetwork
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodenetwork module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, Union, Dict, Any

import requests

from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup


if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class ApiNodeNetwork(RestApiGroup):
    """
        Interface layer for REST operations on network configuration.
    """
    
    def get_configuration(self, aspects: Optional[AspectsRest] = None) -> Dict[str, Any]:
        """
            Retrieves the full network configuration.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: Dictionary of network configuration values.
        """
        leaf = "restapi/network/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        return resp.json()

    def get_value(self, key: str, aspects: Optional[AspectsRest] = None) -> Any:
        """
            Retrieves a specific network configuration value.
            
            :param key: The configuration key/path to retrieve.
            :param aspects: Optional REST call aspects configuration.
            
            :returns: The value of the key.
        """
        leaf = f"restapi/network/{key}/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        return resp.json()

    def set_value(self, key: str, value: Any, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Sets a specific network configuration value.
            
            :param key: The configuration key/path to set.
            :param value: The new value.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = f"restapi/network/{key}/"
        client: "DliPowerRestClient" = self.client
        
        client.perform_call(leaf, method="PUT", json=value, aspects=aspects)
        return True
    
    def update(self, settings: Dict[str, Any], aspects: Optional[AspectsRest] = None) -> bool:
        """
            Updates multiple network configuration values using PATCH and JSON Patch.
            
            :param settings: Dictionary of settings to update.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = "restapi/network/"
        client: "DliPowerRestClient" = self.client
        
        patch_ops = []
        for k, v in settings.items():
            patch_ops.append({
                "op": "add", # Using add/replace strategy
                "path": f"/{k}",
                "value": v
            })
            
        headers = {"Content-Type": "application/json-patch+json"}
        client.perform_call(leaf, method="PATCH", json=patch_ops, headers=headers, aspects=aspects)
        return True

