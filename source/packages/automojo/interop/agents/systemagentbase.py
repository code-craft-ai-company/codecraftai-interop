
"""
    .. module:: systemagentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module defining :class:`SystemAgentBase` which is the base class
        for agents that execute system commands on a device.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
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
