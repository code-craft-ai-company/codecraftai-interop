__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.protocols.upnp.model.devices.upnprootdevice import UpnpRootDevice

from automojo.interop.protocols.upnp.model.upnpdevicedetail import UpnpDeviceDetail

class UpnpAgent(UpnpRootDevice):

    def __init__(self, device_detail: UpnpDeviceDetail):
        super().__init__(device_detail)
        return
