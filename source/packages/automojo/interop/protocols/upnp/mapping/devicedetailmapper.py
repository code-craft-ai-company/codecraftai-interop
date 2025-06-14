

"""
.. module:: devicedetailmapper
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: devicedetailmapper module.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Any, Dict, List, Optional, Type

import logging

logger = logging.getLogger()

from xml.etree.ElementTree import Element

from automojo.interop.protocols.upnp.model.description.basic1devicedesc import Basic1DeviceDesc
from automojo.interop.protocols.upnp.model.description.embeddeddevicedesc import EmbeddedDeviceDesc
from automojo.interop.protocols.upnp.model.description.icondesc import IconDesc
from automojo.interop.protocols.upnp.model.description.serviceevidence import ServiceEvidence
from automojo.interop.protocols.upnp.model.description.specversion import SpecVersion

from automojo.interop.protocols.upnp.constants import (
    UPNP_DEVICE1_NAMESPACE_PREFIX,
    UPNP_DEVICE1_NAMESPACE_PREFIX_END
)

class DeviceDetailMapper:
    """
        A :class:`DeviceDetailMapper` object is an object that assists the :class:`DeviceQueryManager` in the processing
        of information queries for devices.
    """

    MANUFACTURER_NAME = ""

    @classmethod
    def create_root_device_description(cls, root_el: Element, namespaces: Dict[str, str], specVersion: SpecVersion,
                                       locationURL: Optional[str] = None) -> Basic1DeviceDesc:
        """
            Creates a device description object from the root device element.
        """

        device_el: Element = root_el.find("device", namespaces=namespaces)

        device_desc = cls._process_device(root_el, device_el, namespaces, specVersion, locationURL=locationURL, is_embedded=False)

        return device_desc


    @classmethod
    def pull_spec_version_and_manufacturer(cls, root_el: Element, namespaces: Dict[str, str]) -> SpecVersion:

        spec_ver = None
        manufacturer = None

        try:
            spec_ver_el = root_el.find("specVersion", namespaces)

            spec_ver = cls._process_spec_version(spec_ver_el, namespaces=namespaces)

            device_el = root_el.find("device", namespaces=namespaces)
            manufacturer_el = device_el.find("manufacturer", namespaces=namespaces)
            manufacturer = manufacturer_el.text

        except Exception as err:
            err_msg = f"Error parsing device description for 'specVersion' and 'device/manufacturer': {err}"
            logger.error(err_msg)

            spec_ver = None
            manufacturer = None
        
        return spec_ver, manufacturer


    @classmethod
    def _create_basic1_device_desc(cls, root_el: Element, device_el: Element, namespaces: Dict[str, str], specVersion: SpecVersion,
                                   locationURL: str, params: Dict[str, Any]) -> Basic1DeviceDesc:
        
        device = Basic1DeviceDesc(specVersion=specVersion, **params, locationURL=locationURL)

        return device

    @classmethod
    def _create_embedded_device_desc(cls, root_el: Element, device_el: Element, namespaces: Dict[str, str], specVersion: SpecVersion,
                                     params: Dict[str, Any]) -> Basic1DeviceDesc:
        
        device = EmbeddedDeviceDesc(specVersion=specVersion, **params)

        return device

    @classmethod
    def _process_device(cls, root_el: Element, device_el: Element, namespaces: Dict[str, str], specVersion: SpecVersion,
                        locationURL: Optional[str] = None, is_embedded: bool = False) -> Basic1DeviceDesc:

        required_elements = ['deviceType', 'friendlyName', 'manufacturer', 'modelName', 'UDN']
        
        device_desc = None
        create_device = None
        
        if not is_embedded:
            create_device = cls._create_basic1_device_desc
        else:
            create_device = cls._create_embedded_device_desc

        params = {}

        for child_el in device_el:
            full_tag = child_el.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                val = None
                if tag == "manufacturer":
                    val = child_el.text
                    manufacturer = val.upper()
                elif tag == "iconList":
                    val = cls._process_icons_list(child_el, namespaces=namespaces)
                elif tag == 'deviceList':
                    val = cls._process_embedded_devices_list(child_el, namespaces=namespaces)
                elif tag == 'serviceList':
                    val = cls._process_services_list(child_el, namespaces=namespaces)
                else:
                    val = child_el.text
                
                if val != None:
                    params[tag] = val

                if tag in required_elements:
                    required_elements.remove(tag)

        if len(required_elements) > 0:
            err_msg = f"Missing required elements in device description: {', '.join(required_elements)}"
            logger.error(err_msg)
            raise ValueError(err_msg)

        device_desc = create_device(root_el, device_el, namespaces, specVersion, locationURL, params)

        return device_desc


    @classmethod
    def _process_icons_list(cls, icons_el: Element, namespaces: Dict[str, str]) -> List[IconDesc]:
        
        iconsList = []

        for nxtEl in icons_el:
            full_tag = nxtEl.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                if tag == "icon":
                    propEl = nxtEl.find("mimetype", namespaces=namespaces)
                    mimetype = propEl.text

                    propEl = nxtEl.find("width", namespaces=namespaces)
                    width = int(propEl.text)

                    propEl = nxtEl.find("height", namespaces=namespaces)
                    height = int(propEl.text)

                    propEl = nxtEl.find("depth", namespaces=namespaces)
                    depth = int(propEl.text)

                    propEl = nxtEl.find("url", namespaces=namespaces)
                    url = propEl.text

                    iconInfo = IconDesc(mimetype=mimetype, width=width, height=height, depth=depth, url=url)
                    iconsList.append(iconInfo)

        return iconsList
    

    @classmethod
    def _process_embedded_devices_list(cls, devices_el: Element, namespaces: Dict[str, str]) -> List[EmbeddedDeviceDesc]:
        
        devicesList = []

        specVersion = None

        for nxtEl in devices_el:
            full_tag = nxtEl.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                if tag == "device":
                    propEl = nxtEl.find("deviceType", namespaces=namespaces)
                    deviceType = propEl.text

                    svcInfo = cls._process_device(nxtEl, nxtEl, namespaces=namespaces, specVersion=specVersion)
                    
                    devicesList.append(svcInfo)
                elif tag == "specVersion":

                    specVersion = cls._process_spec_version(nxtEl, namespaces=namespaces)

        return devicesList


    @classmethod
    def _process_services_list(cls, services_el: Element, namespaces: Dict[str, str]) -> List[ServiceEvidence]:
        
        servicesList = []

        for nxtEl in services_el:
            full_tag = nxtEl.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                if tag == "service":
                    propEl = nxtEl.find("serviceType", namespaces=namespaces)
                    serviceType = propEl.text

                    propEl = nxtEl.find("serviceId", namespaces=namespaces)
                    serviceId = propEl.text

                    propEl = nxtEl.find("SCPDURL", namespaces=namespaces)
                    SCPDURL = propEl.text

                    propEl = nxtEl.find("controlURL", namespaces=namespaces)
                    controlURL = propEl.text

                    propEl = nxtEl.find("eventSubURL", namespaces=namespaces)
                    eventSubURL = propEl.text

                    svcInfo = ServiceEvidence(serviceType=serviceType, serviceId=serviceId, controlURL=controlURL, eventSubURL=eventSubURL, SCPDURL=SCPDURL)
                    
                    servicesList.append(svcInfo)

        return servicesList

    @classmethod
    def process_spec_version(cls, spec_ver_el: Element, namespaces: Dict[str, str]) -> SpecVersion:
        
        major = int(spec_ver_el.find("major", namespaces=namespaces).text)
        minor = int(spec_ver_el.find("minor", namespaces=namespaces).text)

        spec_ver = SpecVersion(major=major, minor=minor)

        return spec_ver

