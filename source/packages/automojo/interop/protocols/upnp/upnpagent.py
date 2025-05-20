__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from automojo.interop.protocols.upnpold.devices.upnprootdevice import UpnpRootDevice


class UpnpAgent(UpnpRootDevice):

    def __init__(self, manufacturer: str, modelNumber: str, modelDescription):
        super().__init__(manufacturer, modelNumber, modelDescription)
        return
