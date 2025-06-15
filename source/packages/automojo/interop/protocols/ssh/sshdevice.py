"""
    .. module:: sshdevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`SshDevice` class.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier

from automojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class SshDevice(LandscapeDevice):
    """
        Represents a device that can be accessed using the SSH protocol.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Initialize an :class:`SshDevice` representing a remote host.

            :param lscape: Owning landscape instance.
            :param coordinator: Coordinator managing this device.
            :param friendly_id: Friendly identifier object.
            :param device_type: Type of device being represented.
            :param device_config: Configuration dictionary for the device.
        """

        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        return

    @property
    def host(self) -> str:
        """
            Hostname or IP address of the device.

            :returns: Device host string.
        """
        return self._host

    @property
    def ssh(self) -> SshAgent:
        """
            :class:`SshAgent` extension associated with the device.

            :returns: The instantiated :class:`SshAgent`.
        """
        ext = self._extensions["network/ssh"]
        return ext

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
