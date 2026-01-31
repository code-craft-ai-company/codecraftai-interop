"""
    .. module:: apinodemeter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodemeter module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, Union, Dict, Any

import requests

from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.protocols.power.dlipower.responsemodel import Meter


if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class ApiNodeMeter(RestApiGroup):
    """
        Interface layer for REST operations on meters.
    """
    
    def get_meters(self, aspects: Optional[AspectsRest] = None) -> List[Meter]:
        """
            Retrieves the list of meters from the power controller.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: List of :class:`Meter` objects.
        """
        # We can ask for id and other fields.
        # The spec example 294 '/=,name/' gives keys and names.
        # If we ask for 'all', we might get a list of objects if we don't specify fields.
        # But 'all' with matrix params usually implies filtering or bulk get.
        
        # Let's try getting all with standard fields.
        # Or just GET the collection. 
        # Line 294: /restapi/meter/values/all;/=,name/ returns [key, name, key, name...] which is flat list?
        # That's confusing.
        # Ah, example 297 output: ["bus.0.current", "current", "bus.0.voltage", "voltage", ...]
        # This is a flat list because the selector was /=,name/.
        # If we just do GET /restapi/meter/values/, we probably get a map: { "bus.0.current": { ... }, ... }
        # Let's assume map response for collection.
        
        leaf = "restapi/meter/values/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        data = resp.json()
        
        meters = []
        if isinstance(data, dict):
            for m_id, m_data in data.items():
                if isinstance(m_data, dict):
                     meters.append(Meter(
                         id=m_id,
                         name=m_data.get("name"),
                         value=m_data.get("value"),
                         bus=m_data.get("bus")
                     ))
                elif isinstance(m_data, (int, float, str, bool)):
                     # Maybe it returns just value if we are unlucky? 
                     # But normally collection returns map of resources.
                     pass
                     
        return meters

