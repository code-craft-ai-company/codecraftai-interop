"""
    .. module:: poweragents
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DliPowerAgent object instances used to communicate with power controllers.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []




class DliPowerAgent:

    def __init__(self, interface, attachment) -> None:
        """
            Creates a :class:`DliPowerAgent` bound to a specific relay outlet.

            :param interface: The interface object used to communicate with the power controller.
            :param attachment: Outlet identifier to control.
        """
        self._interface = interface
        self._attachment = attachment
        return

    def on(self) -> bool:
        """
            Turns the attached outlet on.
        """
        success = self._interface.on(outlet=self._attachment)
        return success

    def off(self) -> bool:
        """
            Turns the attached outlet off.
        """
        success = self._interface.off(outlet=self._attachment)
        return success
