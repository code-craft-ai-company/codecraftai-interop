
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
    
    critical: bool
    locked: bool
    name: str
    transient_state: bool
    state: bool
    physical_state: bool
    cycle_delay: Optional[float] = None

