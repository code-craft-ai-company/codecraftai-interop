"""
    .. module:: poweragents
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerAgent object instances used to communicate with power controllers.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

import weakref

if TYPE_CHECKING:
    from automojo.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class DliPowerOutletControl:
    """
        Simple wrapper for controlling a Digital Loggers power relay outlet.
    """

    def __init__(self, client: "DliPowerRestClient", outlet: str) -> None:
        """
            Creates a :class:`DliPowerOutletControl` bound to a specific relay outlet.

            :param client: The client object used to communicate with the power controller.
            :param outlet: The Outlet identifier to control.
        """
        self._client_ref = weakref.ref(client)
        self._outlet = outlet
        return

    @property
    def client(self) -> "DliPowerRestClient":
        """
            Returns a hard reference to the rest client.
        """
        return self._client_ref()

    def on(self) -> bool:
        """
            Turns the attached outlet on.

            :returns: ``True`` if the outlet was successfully turned on.
        """
        success = self.client.on(outlet=self._outlet)
        return success

    def off(self) -> bool:
        """
            Turns the attached outlet off.

            :returns: ``True`` if the outlet was successfully turned off.
        """
        success = self.client.off(outlet=self._outlet)
        return success
