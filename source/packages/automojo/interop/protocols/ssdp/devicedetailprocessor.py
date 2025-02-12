"""
.. module:: manufacturerhints
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the base :class:`ManufacturerHints` object that can be derived in order to customize
               the processing of manufacturer specific data fields.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Any, Dict, List

import logging

logger = logging.getLogger()

from xml.etree.ElementTree import Element

from automojo.interop.protocols.ssdp.model import (
    DeviceDetail,
    EmbeddedDeviceInfo,
    IconInfo,
    ServiceInfo,
    SpecVersion
)

from automojo.interop.protocols.ssdp.constants import (
    UPNP_DEVICE1_NAMESPACE_PREFIX,
    UPNP_DEVICE1_NAMESPACE_PREFIX_END
)

class DeviceDetailProcessor:
    """
        A :class:`DeviceDetailProcessor` object is an object that assists the :class:`DeviceQueryManager` in the processing
        of information queries for devices.
    """

    @classmethod
    def create_upnp_device_1_device(cls, root_el: Element, device_el: Element, namespaces: Dict[str, str], params: Dict[str, Any]) -> DeviceDetail:
        device = DeviceDetail(**params)
        return device

    @classmethod
    def process_device(self, root_el: Element, device_el: Element, namespaces: Dict[str, str], hints: Dict[str, "DeviceDetailProcessor"]) -> DeviceDetail:

        required_elements = ['deviceType', 'friendlyName', 'manufacturer', 'modelName', 'UDN']
        
        devdetail = None
        manufacturer = None

        extra_props = {}

        params = {
            'manufacturerURL': None,
            'modelDescription': None,
            'modelNumber': None,
            'modelURL': None,
            'presentationURL': None,
            'serialNumber': None,
            'UPC': None,
            'iconList': [],
            'deviceList': [],
            'serviceList': [],
            'extra': extra_props
        }

        extra_props = {}

        for child_el in device_el:
            full_tag = child_el.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                val = None
                if tag == "manufacturer":
                    val = child_el.text
                    manufacturer = val.upper()
                elif tag == "iconList":
                    val = DeviceDetailProcessor.process_icons_list(root_el, child_el, namespaces=namespaces)
                elif tag == 'deviceList':
                    val = DeviceDetailProcessor.process_devices_list(root_el, child_el, namespaces=namespaces)
                elif tag == 'serviceList':
                    val = DeviceDetailProcessor.process_services_list(root_el, child_el, namespaces=namespaces)
                else:
                    val = child_el.text
                
                if val != None:
                    params[tag] = val

            else:
                content = child_el.text
                extra_props[full_tag] = content

        if manufacturer is not None:
            if manufacturer in hints:
                hintsobj = hints[manufacturer]

                devdetail = hintsobj.create_upnp_device_1_device(root_el, device_el, namespaces, params)
            else:
                devdetail = DeviceDetailProcessor.create_upnp_device_1_device(root_el, device_el, namespaces, params)
        else:
            warnmsg = "Received an SSDP response that did not have a 'manufacturer' field."
            logger.warn(warnmsg)

        return devdetail

    @classmethod
    def process_icons_list(self, root_el: Element, icons_el: Element, namespaces: Dict[str, str]) -> List[IconInfo]:
        
        iconsList = []

        for nxtEl in icons_el:
            full_tag = nxtEl.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                if tag == "icon":
                    propEl = nxtEl.find("mimetype", namespaces=namespaces)
                    mimetype = propEl.text

                    propEl = nxtEl.find("mimetype", namespaces=namespaces)
                    width = int(propEl.text)

                    propEl = nxtEl.find("mimetype", namespaces=namespaces)
                    height = int(propEl.text)

                    propEl = nxtEl.find("mimetype", namespaces=namespaces)
                    depth = int(propEl.text)

                    propEl = nxtEl.find("url", namespaces=namespaces)
                    url = propEl.text

                    iconInfo = IconInfo(mimetype=mimetype, width=width, height=height, depth=depth, url=url)
                    iconsList.append(iconInfo)

        return iconsList
    
    @classmethod
    def process_devices_list(self, root_el: Element, devices_el: Element, namespaces: Dict[str, str]) -> List[EmbeddedDeviceInfo]:
        
        devicesList = []

        for nxtEl in devices_el:
            full_tag = nxtEl.tag

            if full_tag.startswith(UPNP_DEVICE1_NAMESPACE_PREFIX):
                tag = full_tag[UPNP_DEVICE1_NAMESPACE_PREFIX_END:]

                if tag == "device":
                    propEl = nxtEl.find("deviceType", namespaces=namespaces)
                    deviceType = propEl.text

                    svcInfo = EmbeddedDeviceInfo(deviceType=deviceType)
                    
                    devicesList.append(svcInfo)

        return devicesList

    @classmethod
    def process_services_list(self, root_el: Element, services_el: Element, namespaces: Dict[str, str]) -> List[ServiceInfo]:
        
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

                    svcInfo = ServiceInfo(serviceType=serviceType, serviceId=serviceId, SCPDURL=SCPDURL,
                                          controlURL=controlURL, eventSubURL=eventSubURL)
                    
                    servicesList.append(svcInfo)

        return servicesList

    @classmethod
    def process_spec_version(self, spec_ver_el: Element, namespaces: Dict[str, str]) -> SpecVersion:

        major = int(spec_ver_el.find("major", namespaces=namespaces).text)
        minor = int(spec_ver_el.find("minor", namespaces=namespaces).text)
        
        sver = SpecVersion(major=major, minor=minor)
        
        return sver