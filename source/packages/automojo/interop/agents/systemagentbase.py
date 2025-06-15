
"""
    .. module:: commandagentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`CommandAgentBase` object which is a base
    class for object that allow running commands via some protocol interface.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from automojo.interop.interfaces.isystemcontext import ISystemContext

class SystemAgentBase(ISystemContext):
    """
        Base class for agents that execute system commands on a device.
    """

    def __init__(self) -> None:
        """
            Initializes the :class:`SystemAgentBase` instance.
        """
        return
