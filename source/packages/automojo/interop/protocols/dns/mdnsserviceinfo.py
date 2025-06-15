

"""
    .. module:: mdnsserviceinfo
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: mdnsserviceinfo module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import os
import socket

class MdnsServiceInfo:
    """Container object describing a discovered mDNS service instance."""

    def __init__(self) -> None:
        """
            Initializes the :class:`MdnsServiceInfo` object.
        """
        self._addresses = []
        self._host_ttl = None
        self._other_ttl = None
        self._interface_index = None
        self._key = None
        self._port = None
        self._priority = None
        self._server = None
        self._properties = {}
        self._server = None
        self._server_key = None
        self._svc_name = None
        self._svc_type = None
        self._text = None
        self._weight = None
        return

    @property
    def addresses(self):
        """List of raw addresses associated with the service."""
        return self._addresses

    @property
    def first_ipv4_address(self):
        """First IPv4 address for the service if one exists."""
        fipv4_addr = None

        for addr in self._addresses:
            if len(addr) == 4: 
                fipv4_addr = socket.inet_ntoa(addr)
                break

        return fipv4_addr

    @property
    def host_ttl(self):
        """Time-to-live value for the host record."""
        return self._host_ttl

    @property
    def interface_index(self):
        """Interface index the service was discovered on."""
        return self._interface_index

    @property
    def key(self):
        """Unique key identifying the service."""
        return self._key
    
    @property
    def other_ttl(self):
        """Time-to-live value for non-host records."""
        return self._other_ttl
    
    @property
    def port(self):
        """Network port for the service."""
        return self._port

    @property
    def priority(self):
        """Service priority value."""
        return self._priority
    
    @property
    def properties(self):
        """Dictionary of TXT record properties."""
        return self._properties
    
    @property
    def server(self):
        """Hostname of the server providing the service."""
        return self._server
    
    @property
    def server_key(self):
        """Key for locating the server record."""
        return self._server_key

    @property
    def svc_name(self):
        """Service instance name."""
        return self._name
    
    @property
    def svc_type(self):
        """Service type string."""
        return self._type

    @property
    def text(self):
        """Raw TXT record payload."""
        return self._text
    
    @property
    def weight(self):
        """Service weight value."""
        return self._weight


    def detail_lines(self):
        """Builds a list of strings describing the service."""

        str_lines = [
            "svc_name: {}".format(self._svc_name),
            "svc_type: {}".format(self._svc_type),
            "ipv4_addr: {}".format(self.first_ipv4_address),
            "properties"
        ]

        svc_props = self.properties

        svc_prop_keys = [k for k in svc_props]
        svc_prop_keys.sort()

        for key in svc_prop_keys:
            val = svc_props[key]
            if isinstance(val, bytes):
                str_lines.append("    {}: {}".format(key, repr(val.decode())))
            else:
                str_lines.append("    {}: {}".format(key, repr(val)))

        return str_lines

    def __str__(self):
        """String representation of the service."""
        
        str_lines = self.detail_lines()
        strval = os.linesep.join(str_lines)

        return strval
