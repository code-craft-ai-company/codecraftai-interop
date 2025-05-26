

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List, Type, TYPE_CHECKING

from automojo.errors.exceptions import AbstractMethodError

from automojo.foundation.extension.extensionprotocolbase import ExtensionProtocolBase
from automojo.interop.protocols.upnp.mapping.devicedetailmapper import DeviceDetailMapper

class UpnpExtensionProtocol(ExtensionProtocolBase):
    """
        Extension protocol for device detail mapper.
    """

    ext_protocol_name = "automojo-interop-upnp-extension-types"

    @classmethod
    def get_device_detail_mapper_types(self) -> List[Type[DeviceDetailMapper]]:
        """
            Returns a list of device detail mappers that are registered with this extension protocol.
        """
        raise AbstractMethodError("The 'get_device_detail_mapper_type' class method must be implemented for this protocol.")
