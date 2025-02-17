"""
.. module:: inetworkclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the `INetworkClient` protocol.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Protocol

class INetworkClient(Protocol):
    """
        The :class:`INetworkClient` interface is used to provide a common interface for network clients.
    """

    @property
    def ipaddr(self) -> str:
        ...