"""
    .. module:: apinodeconfig
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodeconfig module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional, Dict, Any, TYPE_CHECKING

import requests

from ccai.restclient.base.aspectsrest import AspectsRest
from ccai.restclient.base.restapigroup import RestApiGroup


if TYPE_CHECKING:
    from ccai.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class ConfigApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on configuration.
    """
    
    def get_all(self, aspects: Optional[AspectsRest] = None) -> Dict[str, Any]:
        """
            Retrieves the full configuration as a dictionary.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: Dictionary of configuration values.
        """
        # Using depth=1 to get immediate children values where possible or references?
        # Spec 188 uses depth=2 for freeform text.
        # Default depth is infinity? No, spec says "Range: dli-depth=infinity" is default.
        # But for JSON, we might get references for sub-objects.
        # Let's just GET the root config.
        leaf = "restapi/config/"
        client: "DliPowerRestClient" = self.client
        
        # Spec says default depth is infinity so we should get everything?
        # But we might want headers to be explicit if needed. 
        # For now, simple GET.
        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=200, aspects=aspects)
        
        rtnval = resp.json()
        return rtnval

    def get_value(self, key: str, aspects: Optional[AspectsRest] = None) -> Any:
        """
            Retrieves a specific configuration value.
            
            :param key: The configuration key to retrieve (e.g. 'hostname', 'http_port').
            :param aspects: Optional REST call aspects configuration.
            
            :returns: The value of the configuration key.
        """
        leaf = f"restapi/config/{key}/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=200, aspects=aspects)
        
        # Responses for scalars are just the value in JSON?
        # Or a "value" object?
        # Spec 4.1 scalar types ... JSON literals. 
        # Example 347: ip_address returns "192.168.0.2" (JSON string).
        
        rtnval = resp.json()
        return rtnval

    def set_value(self, key: str, value: Any, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Sets a specific configuration value.
            
            :param key: The configuration key to set.
            :param value: The new value.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = f"restapi/config/{key}/"
        client: "DliPowerRestClient" = self.client
        
        # Use PUT to create or overwrite.
        # Section 5.4.1 JSON is main interchange.
        # Can we send raw JSON value or object?
        
        import json
        headers = {"Content-Type": "application/json"}
        body_content = json.dumps(value)
        
        client.perform_call(leaf=leaf, method="PUT", params=None, body=body_content, headers=headers, exp_status=[200, 204], aspects=aspects)
        return True

    def update(self, settings: Dict[str, Any], aspects: Optional[AspectsRest] = None) -> bool:
        """
            Updates multiple configuration values using PATCH.
            
            :param settings: Dictionary of settings to update.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = "restapi/config/"
        client: "DliPowerRestClient" = self.client
        
        # Let's construct a JSON Patch.
        patch_ops = []
        for k, v in settings.items():
            patch_ops.append({
                "op": "add", # or replace. spec 7.5 says replace is functionally identical to remove+add.
                             # But usually "replace" is safer for existing keys.
                             # However, if key allows 'add', replace works?
                             # Let's use 'replace' for config values.
                "path": f"/{k}",
                "value": v
            })
            
        import json
        headers = {"Content-Type": "application/json-patch+json"}
        body_content = json.dumps(patch_ops)
        
        client.perform_call(leaf=leaf, method="PATCH", params=None, body=body_content, headers=headers, exp_status=[200, 204], aspects=aspects)
        return True


