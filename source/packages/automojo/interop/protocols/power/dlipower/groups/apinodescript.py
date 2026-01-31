"""
    .. module:: apinodescript
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodescript module.

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

class ApiNodeScript(RestApiGroup):
    """
        Interface layer for REST operations on scripting.
    """
    
    def start_script(self, function_name: str, source: Optional[str] = None, aspects: Optional[AspectsRest] = None) -> str:
        """
            Starts a scripting function.
            
            :param function_name: The name of the user function to run.
            :param source: Optional source code or call string (e.g. 'test(1.5, "hello")').
            :param aspects: Optional REST call aspects configuration.
            
            :returns: The thread identifier as a string.
        """
        leaf = "restapi/script/start/"
        client: "DliPowerRestClient" = self.client
        
        # Spec says input is a list of objects?
        # Example 333: --data-binary '[{"user_function":"test"}]'
        # Example 339: --data-binary '[{"user_function":"test","source":"test(1.5,\"hello\")"}]'
        
        item = {"user_function": function_name}
        if source:
            item["source"] = source
            
        payload = [item]
        
        # Spec says Content-Type: application/json
        # client.perform_call with json=payload should handle it.
        
        resp: requests.Response = client.perform_call(leaf, method="POST", json=payload, aspects=aspects)
        
        # Result is a JSON string, e.g. "11"
        return resp.json()

