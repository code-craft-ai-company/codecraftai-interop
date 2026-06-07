"""
    .. module:: inetworkclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the `INetworkClient` protocol.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Protocol

class INetworkClient(Protocol):
    """
        The :class:`INetworkClient` interface is used to provide a common interface for network clients.
    """

    @property
    def ipaddr(self) -> str:
        """
            Returns the IPv4 or IPv6 address for this network client.

            :returns: The IP address associated with the client.
        """
        ...
