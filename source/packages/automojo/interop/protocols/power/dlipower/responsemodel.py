
"""
    .. module:: responsemodel
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: responsemodel module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional


from dataclasses import dataclass


@dataclass
class Outlet:
    """
        Data model representing a single outlet on the power controller.

        :param critical: Indicates if the outlet is marked as critical.
        :param locked: Indicates if the outlet is locked from changes.
        :param name: Human-readable name for the outlet.
        :param transient_state: Pending state transition flag.
        :param state: Current on/off state.
        :param physical_state: Actual hardware state.
        :param cycle_delay: Optional delay for cycling operations.
    """

    critical: bool
    locked: bool
    name: str
    transient_state: bool
    state: bool
    physical_state: bool
    cycle_delay: Optional[float] = None

