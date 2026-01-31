"""
    .. module:: apinodeautoping
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinodeautoping module.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Optional, Union, Dict, Any

import requests

from automojo.restclient.base.aspectsrest import AspectsRest
from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.protocols.power.dlipower.responsemodel import AutoPingItem


if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class AutopingApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on autoping.
    """
    
    def get_items(self, aspects: Optional[AspectsRest] = None) -> List[AutoPingItem]:
        """
            Retrieves the list of autoping items from the power controller.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: List of :class:`AutoPingItem` objects.
        """
        # Assuming collection is 'items' based on standard patterns and spec hints
        leaf = "restapi/autoping/items/all/" 
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        data = resp.json()
        
        items = []
        if isinstance(data, list):
            for item_data in data:
                if isinstance(item_data, dict):
                    # Mapping generic fields if possible. 
                    # Spec is vague, so we use safe accesses.
                    items.append(AutoPingItem(
                        enabled=item_data.get("enabled", False),
                        host=item_data.get("host"),
                        outlets=item_data.get("outlets"),
                        status=item_data.get("status")
                    ))
        
        return items

    def set_item(self, item: AutoPingItem, item_id: str, aspects: Optional[AspectsRest] = None) -> bool:
        """
            Updates an autoping item.
            
            :param item: The item data to update.
            :param item_id: The ID of the item to update.
            :param aspects: Optional REST call aspects configuration.
        """
        leaf = f"restapi/autoping/items/{item_id}/"
        client: "DliPowerRestClient" = self.client
        
        payload = {
            "enabled": item.enabled,
        }
        if item.host is not None:
             payload["host"] = item.host
        if item.outlets is not None:
             payload["outlets"] = item.outlets
             
        client.perform_call(leaf, method="PUT", data=payload, aspects=aspects)
        return True

