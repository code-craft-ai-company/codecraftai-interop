
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from http import HTTPStatus

from xml.etree.ElementTree import fromstring as parse_xml_content

import requests

from automojo.interop.protocols.ssdp.manufacturers.bose.bosedetailprocessor import BoseDetailProcessor
from automojo.interop.protocols.ssdp.manufacturers.bose.constants import MANUFACTURER_NAME as BOSE_MANUFACTURER_NAME

from automojo.interop.protocols.ssdp.constants import UPNP_DEVICE1_NAMESPACE
from automojo.interop.protocols.ssdp.devicedetailprocessor import DeviceDetailProcessor

class DeviceQueryManager:

    MANUFACTURER_HINTS = {
        BOSE_MANUFACTURER_NAME: BoseDetailProcessor
    }

    def __init__(self):
        return
    
    def query_device_details(self, location: str):

        details = None

        try:
            resp = requests.get(location, timeout=2)
            if resp.status_code == HTTPStatus.OK:
                try:
                    default_namespaces = {"": UPNP_DEVICE1_NAMESPACE}
                    xml_content = resp.content.decode("utf-8")
                    root_el = parse_xml_content(xml_content)
                    
                    spec_ver_el = root_el.find("specVersion", default_namespaces)
                    sver = DeviceDetailProcessor.process_spec_version(spec_ver_el, default_namespaces)
                    
                    device_el = root_el.find("device", namespaces=default_namespaces)
                    device = DeviceDetailProcessor.process_device(root_el, device_el, default_namespaces, self.MANUFACTURER_HINTS)
                    
                except Exception as parse_err:
                    pass
        except Exception as req_err:
            pass

        return details
    
    
