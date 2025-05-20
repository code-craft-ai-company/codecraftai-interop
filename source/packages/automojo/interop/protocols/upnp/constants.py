
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import platform

UPNP_DEVICE1_NAMESPACE = "urn:schemas-upnp-org:device-1-0"
UPNP_DEVICE1_NAMESPACE_PREFIX = "{" + UPNP_DEVICE1_NAMESPACE + "}"

UPNP_DEVICE1_NAMESPACE_PREFIX_END = len(UPNP_DEVICE1_NAMESPACE_PREFIX)

UPNP_DEFAULT_SEARCH_WINDOW_LENGTH = float(20)
UPNP_DEFAULT_SEARCH_MONITOR_INTERVAL = float(2)

TIMEDELTA_RENEWAL_WINDOW = 120

class UPNP_HEADERS:
    USER_AGENT = "AutomationMojo/1.0 UPNP Test Package"
    SERVER = "{},{},AutomationKit/1.0".format(platform.system(), platform.release())
