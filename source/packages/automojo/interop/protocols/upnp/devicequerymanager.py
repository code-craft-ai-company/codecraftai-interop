
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional

import logging
import os

from http import HTTPStatus
from xml.etree.ElementTree import fromstring as parse_xml_content

import requests

from automojo.interop.protocols.upnp.constants import UPNP_DEVICE1_NAMESPACE
from automojo.interop.protocols.upnp.mapping.devicedetailmapper import DeviceDetailMapper

from automojo.interop.protocols.upnp.model.description.basic1devicedesc import Basic1DeviceDesc

from automojo.interop.protocols.upnp.wellknown import DeviceDetailMapperRegistrySingleton

logger = logging.getLogger()

class DeviceQueryManager:
    """
        The :class:`DeviceQueryManager` is a class that manages the querying of device details from UPnP devices.  It is used
        by the :class:`UpnpSearchWindow`to queery device for thier device descriptions in order to provide the additional information
        needed to combine the :class:`UpnpDeviceEvidence` and UpnpDeviceDescription into a a :class:`UpnpDeviceDetail` object.
    """

    def __init__(self):
        self._mapper_registry = DeviceDetailMapperRegistrySingleton()
        return

    def query_device_details(self, location: str) -> Optional[Basic1DeviceDesc]:

        device_desc = None

        try:
            resp: requests.Response = requests.get(location, timeout=2)

            if resp.status_code == HTTPStatus.OK:
                try:
                    default_namespaces = {"": UPNP_DEVICE1_NAMESPACE}
                    xml_content = resp.content.decode("utf-8")
                    root_el = parse_xml_content(xml_content)
                    
                    spec_ver, manufacturer = DeviceDetailMapper.pull_spec_version_and_manufacturer(root_el, default_namespaces)
                    
                    if spec_ver is not None and manufacturer is not None:

                        mapper = self._mapper_registry.lookup_device_detail_mapper(manufacturer)
                        
                        device_desc = mapper.create_root_device_description(root_el, default_namespaces, spec_ver, locationURL=location)
                    
                except Exception as parse_err:
                    err_msg = f"Error parsing device description XML: {parse_err}"
                    logger.error(err_msg)

        except Exception as req_err:
            err_msg_lines = [
                f"Error querying device at {location}:"
            ]
            err_msg_lines.extend(f"{req_err}".splitlines(False))

            err_msg = os.linesep.join(err_msg_lines)
            logger.error(err_msg)

        return device_desc
