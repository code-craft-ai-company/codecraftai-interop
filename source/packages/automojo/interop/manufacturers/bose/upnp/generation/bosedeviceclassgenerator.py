
from automojo.interop.manufacturers.bose.constants import BOSE_MANUFACTURER_NAME

from automojo.interop.protocols.upnp.generation.upnpdeviceclassgenerator import UpnpDeviceClassGenerator

class BoseDeviceClassGenerator(UpnpDeviceClassGenerator):
    """
        Implementation of the :class:`UpnpDeviceClassGenerator` for Bose manufactured devices.
    """

    MANUFACTURER_NAME = BOSE_MANUFACTURER_NAME

