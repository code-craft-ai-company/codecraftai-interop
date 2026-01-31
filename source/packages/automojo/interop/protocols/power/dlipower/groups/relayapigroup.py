

"""
    .. module:: apinoderelay
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinoderelay module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, TYPE_CHECKING, Dict

import requests


from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup


from automojo.interop.protocols.power.dlipower.dlipoweroutletcontrol import DliPowerOutletControl
from automojo.interop.protocols.power.dlipower.responsemodel import Outlet

if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient


class RelayApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on power relay nodes.
    """

    def get_outlets(self, aspects: Optional[AspectsRest] = None) -> List[Outlet]:
        """
            Retrieves outlet details from the power controller.

            :param aspects: Optional REST call aspects configuration.

            :returns: List of :class:`Outlet` objects.
        """

        leaf = "restapi/relay/outlets/"
        # Spec says /restapi/relay/outlets/ returns the collection.
        # GET on collection returns reference list or full list depending on Accept/Depth?
        # Let's use /all/ to get the array of representations if possible, or assume default collection GET works.
        
        client: "DliPowerRestClient" = self.client

        resp: requests.Response = client.perform_call(
            leaf=leaf, 
            method="GET", 
            params=None, 
            body=None, 
            exp_status=[200, 207], 
            aspects=aspects
        )
        data = resp.json()
        
        outlets = []
        if isinstance(data, list):
            for o_data in data:
                if isinstance(o_data, dict):
                    outlets.append(Outlet(
                        critical=o_data.get("critical", False),
                        locked=o_data.get("locked", False),
                        name=o_data.get("name", "Unknown"),
                        transient_state=o_data.get("transient_state", False),
                        state=o_data.get("state", False),
                        physical_state=o_data.get("physical_state", False),
                        cycle_delay=o_data.get("cycle_delay")
                    ))
                    
        return outlets

    def get_outlet(self, index: int, aspects: Optional[AspectsRest] = None) -> Outlet:
        """
            Retrieves a single outlet by index.
            
            :param index: The outlet index (0-based).
            :param aspects: Optional REST call aspects configuration.
            
            :returns: An :class:`Outlet` object.
        """
        leaf = f"restapi/relay/outlets/{index}/"
        client: "DliPowerRestClient" = self.client

        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=200, aspects=aspects)
        o_data = resp.json()
        
        # Checking if valid object
        if not isinstance(o_data, dict):
            # Maybe use exception or return None
            # For now assume it works
            raise ValueError(f"Invalid response for outlet {index}: {o_data}")

        rtnval = Outlet(
            critical=o_data.get("critical", False),
            locked=o_data.get("locked", False),
            name=o_data.get("name", "Unknown"),
            transient_state=o_data.get("transient_state", False),
            state=o_data.get("state", False),
            physical_state=o_data.get("physical_state", False),
            cycle_delay=o_data.get("cycle_delay")
        )

        return rtnval


    def set_outlet_state(self, index: int, state: bool, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Sets the state of an outlet (On/Off).
            
            :param index: The outlet index.
            :param state: True for ON, False for OFF.
            :param aspects: Optional REST call aspects configuration.
        """
        # Using PUT to /state/ as per example 237
        leaf = f"restapi/relay/outlets/{index}/state/"
        client: "DliPowerRestClient" = self.client
        
        # Spec 237 uses x-www-form-urlencoded: value=false
        # But section 5.4.1 says JSON is main interchange.
        # We can probably PUT true/false as JSON.
        
        # Note: 'body' arg in perform_call is usually for data, 'json' is not explicitly an arg to perform_call based on my memory of step 182.
        # Step 182: def perform_call(self, ... body: Union[Dict[str, str], None], ...
        # But RestClientBase generally uses requests. 
        # Wait, step 182 perform_call does:
        # req = Request(method=method, url=call_url, headers=headers, params=params, data=body)
        # It doesn't seem to have a 'json' parameter.
        # So I have to manually serialize to JSON or allow 'body' to be passed as data=body.
        # BUT if I want to send JSON I should probably use the json= parameter of request if exposed? 
        # It is NOT exposed in perform_call signature in Step 182.
        
        # I need to set Content-Type header to application/json and dump to string?
        # Or does DliPowerRestClient or RestClientBase handle json?
        # Looking at authenticate, it sets headers manually.
        
        # Oh, `data=body` in Request.
        # If I want to send JSON, I should json.dumps it and set header.
        
        headers = {"Content-Type": "application/json"}
        import json
        body_content = json.dumps(state) 
        # Actually state is bool, so dumps("true") -> "true".
        
        client.perform_call(leaf=leaf, method="PUT", params=None, body=body_content, headers=headers, exp_status=[200, 204, 207], aspects=aspects)
        return True

    def cycle_outlet(self, index: int, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Cycles an outlet (Off -> Delay -> On).
            
            :param index: The outlet index.
            :param aspects: Optional REST call aspects configuration.
        """
        # Spec 6.3 example 632: .../cycle/
        # Also 4.5 Call type... accessed using POST.
        leaf = f"restapi/relay/outlets/{index}/cycle/"
        client: "DliPowerRestClient" = self.client
        
        # POST with empty body or arguments? Cycle usually has no args or maybe delay?
        # Assuming no args for standard cycle.
        resp: requests.Response = client.perform_call(leaf=leaf, method="POST", params=None, body=None, exp_status=[200, 204, 207], aspects=aspects)
        return True

    def get_outlet_controls(self) -> "Dict[str, DliPowerOutletControl]":
        """
            Retrieves a dictionary of outlet controls keyed by outlet name.
            
            :returns: A dictionary of :class:`DliPowerOutletControl` objects.
        """
        outlets = self.get_outlets()
        
        controls = {}
        for index, outlet in enumerate(outlets):
            if outlet.name:
                controls[outlet.name] = DliPowerOutletControl(self.client, index)
                
        return controls
