
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


@dataclass
class User:
    """
        Data model representing a user on the power controller.
        
        :param name: Username.
        :param is_allowed: Whether the user is allowed login.
        :param is_admin: Whether the user has admin privileges.
        :param outlet_access: List of booleans corresponding to outlet access permissions.
        :param password: Password (only when creating/updating, usually not returned in full).
    """
    name: str
    is_allowed: bool
    is_admin: bool
    outlet_access: list[bool]
    password: Optional[str] = None


@dataclass
class AutoPingItem:
    """
        Data model representing an AutoPing item.
        
        :param enabled: Whether the autoping is enabled.
        :param host: Host or IP to ping.
        :param outlets: Associated outlets.
        :param status: Current status.
    """
    enabled: bool
    host: Optional[str] = None
    outlets: Optional[list[int]] = None
    status: Optional[str] = None


@dataclass
class Meter:
    """
        Data model representing a meter.
        
        :param id: The identifier of the meter (e.g. 'bus.0.current').
        :param name: Human-readable name.
        :param value: Current value.
        :param bus: Associated bus index.
    """
    id: str
    name: Optional[str] = None
    value: Optional[float] = None
    bus: Optional[int] = None
