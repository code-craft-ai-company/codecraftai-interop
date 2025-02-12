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

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        return

    @property
    def host(self) -> str:
        return self._host

    @property
    def ssh(self) -> SshAgent:
        ext = self._extensions["network/ssh"]
        return ext

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
