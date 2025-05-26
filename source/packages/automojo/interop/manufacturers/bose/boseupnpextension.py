
from typing import List, Type


from automojo.interop.protocols.upnp.upnpextensionprotocol import UpnpExtensionProtocol
from automojo.interop.protocols.upnp.mapping.devicedetailmapper import DeviceDetailMapper

from automojo.interop.manufacturers.bose.mapping.bosedevicedetailmapper import BoseDeviceDetailMapper

class BoseUpnpExtensionProtocol(UpnpExtensionProtocol):
    """
        Extension protocol for Bose devices.
    """

    @classmethod
    def get_device_detail_mapper_types(self) -> List[Type[DeviceDetailMapper]]:
        """
            Returns a list of device detail mappers that are registered with this extension protocol.
        """
        types = [ BoseDeviceDetailMapper ]
        return types
    
