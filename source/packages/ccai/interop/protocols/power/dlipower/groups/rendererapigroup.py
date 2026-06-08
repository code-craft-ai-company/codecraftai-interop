"""
    .. module:: apinoderenderer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: apinoderenderer module.

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
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=200, aspects=aspects)
        
        rtnval = resp.json()
        return rtnval

    def get_known_image_formats(self, aspects: Optional[AspectsRest] = None) -> Dict[str, str]:
        """
            Retrieves known image formats supported by the renderer.
            
            :param aspects: Optional REST call aspects configuration.
            
            :returns: Dictionary of known image formats (e.g. {'svg': 'SVG', ...}).
        """
        leaf = "restapi/renderer/known_image_formats/"
        client: "DliPowerRestClient" = self.client
        
        resp: requests.Response = client.perform_call(leaf=leaf, method="GET", params=None, body=None, exp_status=200, aspects=aspects)
        
        rtnval = resp.json()
        return rtnval


