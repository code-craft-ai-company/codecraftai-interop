"""
    .. module:: apinodeconfig
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodeconfig module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, Union, Dict, Any, AnyStr

import requests

from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup


if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

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
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        return resp.json()

    def get_value(self, key: str, aspects: Optional[AspectsRest] = None) -> Any:
        """
            Retrieves a specific configuration value.
            
            :param key: The configuration key to retrieve (e.g. 'hostname', 'http_port').
            :param aspects: Optional REST call aspects configuration.
            
            :returns: The value of the configuration key.
        """
        leaf = f"restapi/config/{key}/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        # Responses for scalars are just the value in JSON?
        # Or a "value" object?
        # Spec 4.1 scalar types ... JSON literals. 
        # Example 347: ip_address returns "192.168.0.2" (JSON string).
        return resp.json()

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
        # Example 237: PUT .../all;/state/ data 'value=false'. This is x-www-form-urlencoded.
        # But we can probably use JSON.
        # If we use JSON, we might send the value directly?
        # "JSON data can be any valid JSON literals, not only objects" (line 477).
        
        # RestClientBase perform_call might serialize 'data' to JSON if 'json' kwarg used.
        # We need to be careful about strict scalar vs object.
        # Let's assume we can send the value as the body if content-type is json.
        
        client.perform_call(leaf, method="PUT", json=value, aspects=aspects)
        return True

    def update(self, settings: Dict[str, Any], aspects: Optional[AspectsRest] = None) -> bool:
        """
            Updates multiple configuration values using PATCH.
            
            :param settings: Dictionary of settings to update.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = "restapi/config/"
        client: "DliPowerRestClient" = self.client
        
        # Section 5.5.1 JSON patch.
        # But section 5.5.2 says form-urlencoded is similar to full representation but only changed values.
        # Can we just PATCH with a partial object?
        # Example 320 uses x-www-form-urlencoded with PATCH.
        # "Requests to patch any objects... you need to supply the patch in the JSON patch format." if complex?
        
        # Most simple configs are likely flat.
        # A simple JSON merge patch (RFC 7396) style might work if they support it, 
        # but the spec explicitly mentions JSON Patch (RFC 6902) which is a list of ops.
        
        # However, line 514 says "JSON patch is the main patch format... Other patch formats can be thought of as if they were reduced to it."
        # Does it support application/merge-patch+json? Not explicitly listed.
        # It supports application/x-www-form-urlencoded for flat updates.
        
        # Let's try sending a simple dict with PATCH, which typical REST clients might serialize as json.
        # If the server supports "Accept: application/json" for input? No, Content-Type.
        # Spec 5.4.1 says application/json is accepted by all resources. 
        # Does it treat a JSON object as a merge patch or just replacement?
        
        # Safer to use iteration and set_value, OR use JSON Patch format if we want atomicity.
        # Given "implement the config APIs", a loop of set_value is safe but slow.
        # Let's try to infer if PATCH with object works.
        # Example 320 uses data string for form-urlencoded.
        
        # If I send a dict as json, it might work if the server is smart.
        # But to be safe efficiently, maybe just loop for now or use the bulk update if verified.
        # I'll implement as a loop of set_value for now to be safe, or just provide `set_value`.
        # Wait, `update` is useful. 
        # I will leave `update` as accepting a dict and sending it as JSON PATCH if possible or just JSON.
        
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
            
        headers = {"Content-Type": "application/json-patch+json"}
        client.perform_call(leaf, method="PATCH", json=patch_ops, headers=headers, aspects=aspects)
        return True

