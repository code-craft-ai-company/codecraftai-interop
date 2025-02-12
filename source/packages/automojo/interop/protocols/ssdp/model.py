"""
.. module:: model
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing various objects for medeling information about devices and thier services.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Dict, List, Optional, Union, TYPE_CHECKING

import weakref


if TYPE_CHECKING:
    from automojo.interop.protocols.ssdp.ssdppresence import SsdpPresence


class SpecVersion:

    def __init__(self, *, major: int, minor: int):
        self._major = major
        self._minor = minor
        return
    
    @property
    def major(self) -> int:
        return self._major
    
    @property
    def minor(self) -> int:
        return self._minor


class EmbeddedDeviceInfo:

    def __init__(self, *, deviceType: str):
        self._deviceType = deviceType
        return

    @property
    def deviceType(self) -> str:
        return self._deviceType


class IconInfo:

    def __init__(self, *, mimetype: str, width: int, height: int, depth: int, url: str):
        self._mimetype = mimetype
        self._width = width
        self._height = height
        self._depth = depth
        self._url = url
        return

    @property
    def depth(self) -> int:
        return self._depth
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def mimetype(self) -> str:
        return self._mimetype

    @property
    def url(self) -> str:
        return self._url
    
    @property
    def width(self) -> int:
        return self._width


class ServiceInfo:

    def __init__(self, *, serviceType: str, serviceId: str, SCPDURL: str, controlURL: str, eventSubURL: str):
        self._serviceType = serviceType
        self._serviceId = serviceId
        self._SCPDURL = SCPDURL
        self._controlURL = controlURL
        self._eventSubURL = eventSubURL
        return

    @property
    def controlURL(self) -> str:
        return self._controlURL
    
    @property
    def eventSubURL(self) -> str:
        return self._eventSubURL

    @property
    def SCPDURL(self) -> str:
        return self._SCPDURL

    @property
    def serviceId(self) -> str:
        return self._serviceId

    @property
    def serviceType(self) -> str:
        return self._serviceType


class DeviceDetail:
    
    def __init__(self, *, deviceType: str, friendlyName: str, manufacturer: str, manufacturerURL: Union[str, None], modelDescription: Union[str, None],
                 modelName: str, modelNumber: Union[str, None], modelURL: Union[str, None], presentationURL: str, UDN: str, iconList: List[IconInfo],
                 serialNumber: Union[str, None], serviceList: List[ServiceInfo], deviceList: List[EmbeddedDeviceInfo], UPC: Union[str, None],
                 mac_addr: Optional[str] = None, generation: Optional[str] = None, codename: Optional[str] = None, color: Optional[str] = None,
                 software_version: Optional[str] = None, extra: Dict[str, str]):
        self._deviceType = deviceType
        self._friendlyName = friendlyName
        self._manufacturer = manufacturer
        self._manufacturerURL = manufacturerURL
        self._modelDescription = modelDescription
        self._modelName = modelName
        self._modelNumber = modelNumber
        self._modelURL = modelURL
        self._presentationURL = presentationURL
        self._UDN = UDN
        self._iconList = iconList
        self._serialNumber = serialNumber
        self._serviceList = serviceList
        self._deviceList = deviceList
        self._UPC = UPC
        
        self._mac_addr = mac_addr
        self._generation = generation
        self._codename = codename
        self._color = color
        self._software_version = software_version

        self._extra = extra
        return
    
    @property
    def codename(self) -> Optional[str]:
        return self._codename
    
    @property
    def color(self) -> Optional[str]:
        return self._color

    @property
    def deviceList(self) -> List[EmbeddedDeviceInfo]:
        return self._deviceList

    @property
    def deviceType(self) -> str:
        return self._deviceType
    
    @property
    def extra(self) -> Dict[str, str]:
        return self._extra
    
    @property
    def friendlyName(self) -> str:
        return self._friendlyName
    
    @property
    def generation(self) -> Union[str, None]:
        return self._generation
    
    @property
    def iconList(self) -> List[IconInfo]:
        return self._iconList
    
    @property
    def mac_addr(self) -> Optional[str]:
        return self._mac_addr

    @property
    def manufacturer(self) -> str:
        return self._manufacturer
    
    @property
    def manufacturerURL(self) -> str:
        return self._manufacturerURL

    @property
    def modelDescription(self) -> str:
        return self._modelDescription
    
    @property
    def modelName(self) -> str:
        return self._modelName

    @property
    def modelNumber(self) -> str:
        return self._modelNumber
    
    @property
    def modelURL(self) -> str:
        return self._modelURL
    
    @property
    def presentationURL(self) -> str:
        return self._presentationURL

    @property
    def serialNumber(self) -> str:
        return self._serialNumber
    
    @property
    def serviceList(self) -> List[ServiceInfo]:
        return self._serviceList

    @property
    def software_version(self) -> str:
        return self._software_version

    @property
    def UDN(self) -> str:
        return self._UDN
    
    @property
    def UPC(self) -> str:
        return self._UPC


class SsdpDevice:

    def __init__(self, *, usn: str, status: str, server: str, location: str, ip: str, other: Dict[str, str], presence: "SsdpPresence"):
        self._usn = usn
        self._status = status
        self._server = server
        self._location = location
        self._ip = ip
        self._other = other
        self._presence_ref = weakref.ref(presence)
        return
    
    @property
    def location(self):
        return self._location
    
    @property
    def other(self):
        return self._other
    
    @property
    def ip(self):
        return self._ip

    @property
    def presence(self) -> "SsdpPresence":
        return self._presence_ref()

    @property
    def server(self):
        return self._server

    @property
    def status(self):
        return self._status

    @property
    def usn(self):
        return self._usn


class SsdpService:
    
    def __init__(self, *, device: str, service: str, location: str, status: str, presence: "SsdpPresence"):
        self._device = device
        self._service = service
        self._location = location
        self._status = status
        self._presence_ref = weakref.ref(presence)
        return

    @property
    def device(self):
        return self._device
    
    @property
    def location(self):
        return self._location
    
    @property
    def presence(self) -> "SsdpPresence":
        return self._presence_ref()

    @property
    def service(self):
        return self._service
    
    @property
    def status(self):
        return self._status
