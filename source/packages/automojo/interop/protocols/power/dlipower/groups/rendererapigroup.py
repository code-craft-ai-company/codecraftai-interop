"""
    .. module:: apinoderenderer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinoderenderer module.

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

class RendererApiGroup(RestApiGroup):
    """
        Interface layer for REST operations on renderer.
    """
    
    def get_info(self, aspects: Optional[AspectsRest] = None) -> Dict[str, Any]:
        """
            Retrieves the renderer object info.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: Dictionary of renderer info.
        """
        leaf = "restapi/renderer/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        return resp.json()

    def get_known_image_formats(self, aspects: Optional[AspectsRest] = None) -> Dict[str, str]:
        """
            Retrieves known image formats supported by the renderer.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: Dictionary of known image formats (e.g. {'svg': 'SVG', ...}).
        """
        leaf = "restapi/renderer/known_image_formats/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf, aspects=aspects)
        
        return resp.json()

