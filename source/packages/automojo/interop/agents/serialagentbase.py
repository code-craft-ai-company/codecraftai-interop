"""
    .. module:: serialagentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`SerialAgentBase` object which is a base
    class for objects that allow for sending commands to a device via a
    serial interface.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from automojo.interop.interfaces.isystemcontext import ISystemContext

class SerialAgentBase(ISystemContext):
    """Base class for agents that interact over a serial connection."""

    def __init__(self) -> None:
        """
            Initializes the :class:`SerialAgentBase` instance.
        """
        return
