"""
    .. module:: poweragents
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerAgent object instances used to communicate with power controllers.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import TYPE_CHECKING

import weakref

if TYPE_CHECKING:
    from ccai.interop.protocols.power.dlipower.dlipowerclient import DliPowerRestClient

class DliPowerOutletControl:
    """
        Simple wrapper for controlling a Digital Loggers power relay outlet.
    """

    def __init__(self, client: "DliPowerRestClient", index: int) -> None:
        """
            Creates a :class:`DliPowerSwitchControl` bound to a specific relay outlet.

            :param client: The client object used to communicate with the power controller.
            :param index: The Outlet index to control.
        """
        self._client_ref = weakref.ref(client)
        self._index = index
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
        success = self.client.relay.set_outlet_state(index=self._index, state=True)
        return success

    def off(self) -> bool:
        """
            Turns the attached outlet off.

            :returns: ``True`` if the outlet was successfully turned off.
        """
        success = self.client.relay.set_outlet_state(index=self._index, state=False)
        return success
