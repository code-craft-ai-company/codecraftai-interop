"""
.. module:: poweragentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`PowerAgentBase` object which is a base
               class for object that allow for controlling the power of devices.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Union

from automojo.errors.exceptions import ConfigurationError

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.basiccredential import BasicCredential


class PowerAgentBase:
    """
    """
    def __init__(self, host: str, credential: BaseCredential):
        self._host = host
        self._credential = credential
        return

    def _lookup_power_interface(self, interface_name: str) -> Union[dict, None]:
        """
            Looks up a power interface by power interface name.
        """
        power_iface = None

        if interface_name in self._power_interfaces:
            power_iface = self._power_interfaces[interface_name]
        else:

            interface_config = self._power_config[interface_name]
            
            powerType = interface_config["powerType"]

            if powerType == "DliPowerSwitch":
                credobj: BasicCredential = self._credential
                power_iface = dlipower.PowerSwitch(userid=credobj.username, password=credobj.password, hostname=self._host)

                self._power_interfaces[interface_name] = power_iface
            else:
                errmsg = "Un-Support power interface type={}.".format(powerType)
                raise ConfigurationError(errmsg) from None

        return power_iface
