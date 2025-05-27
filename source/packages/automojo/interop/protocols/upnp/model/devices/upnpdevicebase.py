"""
.. module:: upnpdevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`UpnpDevice` class and associated diagnostic.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, Union, TYPE_CHECKING

import threading
import weakref

from xml.etree.ElementTree import fromstring as xml_fromstring
from xml.etree.ElementTree import Element

import requests

from automojo.foundation.fspath import normalize_name_for_path

from automojo.interop.protocols.upnp.model.upnpdevicedetail import UpnpDeviceDetail

from automojo.interop.protocols.upnp.upnperrors import UpnpServiceNotAvailableError

from automojo.interop.protocols.upnp.model.services.upnpserviceproxy import UpnpServiceProxy

from automojo.interop.protocols.upnp.model.evidence.upnpdeviceevidence import UpnpDeviceEvidence
from automojo.interop.protocols.upnp.model.description.basic1devicedesc import Basic1DeviceDesc


# Types imported only for type checking purposes
if TYPE_CHECKING:
    from automojo.interop.protocols.upnp.model.devices.upnpdevicefactory import UpnpDeviceFactory


UPNP_SERVICE1_NAMESPACE = "urn:schemas-upnp-org:service-1-0"


class UpnpDeviceBase:
    """
        The UPNP Root device is the base device for the hierarchy that is
        associated with a unique network devices location.  The :class:`RootDevice`
        and its subdevices are linked by thier location url.

        http://www.upnp.org/specs/arch/UPnP-arch-DeviceArchitecture-v1.0.pdf
    """

    MANUFACTURER = "unknown"
    MODEL_NUMBER = "unknown"
    MODEL_DESCRIPTION = "unknown"

    def __init__(self, device_detail: UpnpDeviceDetail):
        """
            Creates a root device object.
        """
        super(UpnpDeviceBase, self).__init__()

        self._device_detail = device_detail
        self._device_description = device_detail.description
        self._device_evidence = device_detail.evidence

        if self.device_description.manufacturer is not None:
            self.MANUFACTURER = self.device_description.manufacturer
        
        if self.device_description.modelNumber is not None:
            self.MODEL_NUMBER = self.device_description.modelNumber

        if self.device_description.modelDescription is not None:
            self.MODEL_DESCRIPTION = self.device_description.modelDescription

        self._host = None
        self._urlBase = None

        self._device_lock = threading.RLock()

        self._embedded_devices = {}
        self._services = {}
        
        # We must have an initial device description in order to be able to create a
        # device instance.   Processes the serviceList and deviceList in the device
        # description to populate the service description and embedded device description
        # lookup tables.
        self._service_descriptions = {}
        serviceList = self._device_description.serviceList
        if serviceList is not None:
            for serviceInfo in serviceList:
                svckey = serviceInfo.get_extension_key()
                self._service_descriptions[svckey] = serviceInfo

        self._embedded_device_descriptions = {}
        deviceList = self._device_description.deviceList
        if deviceList is not None:
            for deviceInfo in self._device_description.deviceList:
                devkey = deviceInfo.get_extension_key()
                self._embedded_device_descriptions[devkey] = deviceInfo

        return

    @property
    def device_description(self) -> Union[Basic1DeviceDesc, None]:
        """
            Returns the device description from the UPNP device.
        """
        return self._device_description

    @property
    def device_detail(self) -> UpnpDeviceDetail:
        """
            Returns the device detail object that contains the device description and evidence.
        """
        return self._device_detail

    @property
    def device_evidence(self) -> UpnpDeviceEvidence:
        """
            Returns the device evidence from the UPNP device.
        """
        return self._device_evidence

    @property
    def host(self) -> str:
        """
            Returns the host associated with the UPNP device.
        """
        return self._host

    @property
    def services(self) -> List[UpnpServiceProxy]:
        """
            Returns a list of service proxies associated with the UPNP device.
        """
        service_list = None

        self._device_lock.acquire()
        try:
            service_list = [svc for svc in self._services.values()]
        finally:
            self._device_lock.release()

        return service_list

    @property
    def services_descriptions(self):
        """
            Returns a table of service descriptions associated with the UPNP device.
        """
        return self._services_descriptions

    @property
    def URLBase(self) -> str:
        """
            Returns the base URL for the UPNP device that is used with any relative URLs in devices or service
            description documents.
        """
        return self._urlBase

    def get_service_description(self, serviceType: str) -> Union[dict, None]:
        """
            Gets the service description for the specified service type.

            :param serviceType: The service type to lookup the service description for.

            :returns: Returns the description information for the service type if found or None if not found.
        """
        svc_content = None

        for nxtsvc in self._device_description.serviceList:
            if nxtsvc.serviceType == serviceType:
                fullurl = self.URLBase.rstrip("/") + "/" + nxtsvc.SCPDURL.lstrip("/")

                resp: requests.Response = requests.get(fullurl)
                if resp.status_code == 200:
                    svc_content = resp.text
                    break

        return svc_content

    def lookup_service(self, service_key: str, allow_none: bool=False, factory: Optional["UpnpDeviceFactory"] = None) -> Union[UpnpServiceProxy, None]:
        """
            Looks up a service proxy based on the service manufacturer and service type specified.

            :param serviceManufacturer: The manufacturer associated with the device and service manufacturer.
            :param serviceType: The service type of the service to lookup.
            :param allow_none: If True, this API will not thrown an exception if the service cannot be found.

            :returns: The service proxy associated with the manufacturer and service type provided or None.
        """
        svc = None

        self._device_lock.acquire()
        try:
            if service_key in self._services:
                svc = self._services[service_key]

            elif factory is not None:
                svc_desc = self._service_descriptions[service_key]

                self._device_lock.release()
                try:
                    svc = factory.create_service_instance(svc_desc)
                finally:
                    self._device_lock.acquire()

                if svc is not None:
                    self._services[service_key] = svc
        finally:
            self._device_lock.release()

        if svc is None and not allow_none:
            errmsg = "The service service_key={} was not found or is not available.".format(service_key)
            raise UpnpServiceNotAvailableError(errmsg)

        return svc

    def as_dict(self, brief=False):
        """
            Creates a dictionary description of the device and its sub devices and services.
        """
        dval = None

        self._device_lock.acquire()
        try:
            desc = self._device_description

            if desc is not None:
                dval = desc.as_dict(brief=brief)

                dval["URLBase"] = self.URLBase

                if not brief:
                    serviceDescList = []
                    serviceList = dval["serviceList"]
                    for svc_info in serviceList:
                        svc_type = svc_info["serviceType"]
                        sdurl = self._urlBase.rstrip("/") + "/" + svc_info["SCPDURL"].lstrip("/")
                        sdesc = self._locked_process_full_service_description(sdurl)
                        sdesc["serviceType"] = svc_type
                        serviceDescList.append(sdesc)

                    dval["serviceDescriptionList"] = serviceDescList
        finally:
            self._device_lock.release()

        return dval

    def to_json(self, brief=False):
        """
            Creates a json description of the device and its sub devices and services.
        """
        json_str = None

        self._device_lock.acquire()
        try:
            desc = self._description

            if desc is not None:
                json_str = self._description.to_json(brief=brief)
        finally:
            self._device_lock.release()

        return json_str

    def _locked_populate_embedded_device_descriptions(self, factory: "UpnpDeviceFactory", description: Basic1DeviceDesc):
        """
            Takes in a device description and processes it for embedded devices.

            :param factory: The UpnpDeviceFactory that has registered exentsion types that is used to instantiate
                            embedded devices when the UPNP device description is processed.
            :param description: The Basic1DeviceDesc object that contains information about the device and its embedded devices.
        """
        # pylint: disable=no-self-use,unused-argument
        raise NotImplementedError("UpnpDevice._populate_embedded_devices: must be overridden.") from None

    def _locked_populate_services_descriptions(self, factory: "UpnpDeviceFactory", description: Basic1DeviceDesc):
        """
            Takes in a device description and processes it for service descriptions.

            :param factory: The UpnpDeviceFactory that has registered exentsion types that is used to instantiate
                            services when the UPNP device description is processed.
            :param description: The Basic1DeviceDesc object that contains information about the device and its services.
        """
        # pylint: disable=protected-access
        for serviceInfo in description.serviceList:
            serviceManufacturer = normalize_name_for_path(serviceInfo.serviceManufacturer)
            serviceType = serviceInfo.serviceType

            svckey = generate_extension_key(serviceManufacturer, serviceType)
            if serviceType not in self._services_descriptions:
                self._services_descriptions[svckey] = serviceInfo

                svc_inst = factory.create_service_instance(serviceManufacturer, serviceType)
                if svc_inst is not None:
                    device_ref = weakref.ref(self)
                    svc_inst._proxy_link_service_to_device(device_ref, serviceInfo)
                    self._services[svckey] = svc_inst
            else:
                svc_inst = self._services[svckey]

        return

    def _locked_process_full_service_description(self, sdurl: str):
        """
            Downloads and processes the service description document.

            :param sdurl: The url of the service description document to process.
        """
        svcdesc = None

        resp = requests.get(sdurl)
        if resp.status_code == 200:
            svcdesc = {}

            namespaces = {"": UPNP_SERVICE1_NAMESPACE}

            try:
                xml_content = resp.text
                descDoc = xml_fromstring(xml_content)

                specVersionNode = descDoc.find("specVersion", namespaces=namespaces)
                verInfo = self._locked_process_node_spec_version(specVersionNode, namespaces=namespaces)
                svcdesc["specVersion"] = verInfo

                serviceStateTableNode = descDoc.find("serviceStateTable", namespaces=namespaces)
                variablesTable, typesTable, eventsTable = self._locked_process_node_state_table(serviceStateTableNode, namespaces=namespaces)
                svcdesc["variablesTable"] = variablesTable
                svcdesc["typesTable"] = typesTable
                svcdesc["eventsTable"] = eventsTable

                actionListNode = descDoc.find("actionList", namespaces=namespaces)
                actionsTable = self._locked_process_node_action_list(actionListNode, namespaces=namespaces)
                svcdesc["actionsTable"] = actionsTable
            except:
                print("Service Description Failure: %s" % sdurl)
                raise

        return svcdesc

    def _locked_process_node_action_list(self, actionListNode: Element, namespaces: Optional[dict] = None) -> dict:
        """
            Processes the node action list and creates a dictionary of the actions supported by the service.

            :param actionListNode: The parent node for all the action list node.
            :param namespaces: A dictionary of namespaces to use when processing the XML.
        """
        # pylint: disable=no-self-use
        actionTable = {}

        actionNodeList = actionListNode.findall("action", namespaces=namespaces)
        for actionNode in actionNodeList:
            actionName = actionNode.find("name", namespaces=namespaces).text
            actionArgs = {}

            argumentListNode = actionNode.find("argumentList", namespaces=namespaces)
            if argumentListNode is not None:
                argumentNodeList = argumentListNode.findall("argument", namespaces=namespaces)
                for argumentNode in argumentNodeList:
                    argName = argumentNode.find("name", namespaces=namespaces).text
                    argDirection = argumentNode.find("direction", namespaces=namespaces).text

                    argRelStateVar = None
                    argRelStateNode = argumentNode.find("relatedStateVariable", namespaces=namespaces)
                    if argRelStateNode is not None:
                        argRelStateVar = argRelStateNode.text

                    actionArgs[argName] = {
                        "name": argName,
                        "direction": argDirection,
                        "relatedStateVariable": argRelStateVar
                        }

            actionTable[actionName] = {
                    "name": actionName,
                    "arguments" : actionArgs
                }

        return actionTable

    def _locked_process_node_spec_version(self, specVersionNode: Element, namespaces: Optional[dict] = None) -> dict:
        # pylint: disable=no-self-use
        verInfo = {}

        verInfo["major"] = specVersionNode.find("major", namespaces=namespaces).text
        verInfo["minor"] = specVersionNode.find("minor", namespaces=namespaces).text

        return verInfo

    def _locked_process_node_state_table(self, serviceStateTableNode: Element, namespaces: Optional[dict] = None) -> dict:
        # pylint: disable=no-self-use
        variablesTable = {}
        typesTable = {}
        eventsTable = {}

        stateVariableList = serviceStateTableNode.findall("stateVariable", namespaces=namespaces)
        for stateVariableNode in stateVariableList:
            name = stateVariableNode.find("name", namespaces=namespaces).text
            dataType = stateVariableNode.find("dataType", namespaces=namespaces).text

            varInfo = { "name": name, "dataType": dataType}
            if name.startswith("A_ARG_TYPE_"):
                typesTable[name] = varInfo
            else:
                variablesTable[name] = varInfo

                sendEvents = "no"
                if "sendEvents" in stateVariableNode.attrib:
                    sendEvents = stateVariableNode.attrib["sendEvents"]

                if sendEvents == "yes":
                    eventsTable[name] = varInfo

        return variablesTable, typesTable, eventsTable
