"""
    .. module:: apinodescript
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodescript module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional, TYPE_CHECKING

import requests

from ccai.restclient.base.aspectsrest import AspectsRest
from ccai.restclient.base.restapigroup import RestApiGroup


if TYPE_CHECKING:
    from ccai.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class ScriptApiGroup(RestApiGroup):
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
        
        import json
        headers = {"Content-Type": "application/json"}
        body_content = json.dumps(payload)
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="POST", params=None, body=body_content, headers=headers, exp_status=200, aspects=aspects)
        
        # Result is a JSON string, e.g. "11"
        rtnval = resp.json()
        return rtnval


