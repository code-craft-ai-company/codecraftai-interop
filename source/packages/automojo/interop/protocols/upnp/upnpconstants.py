__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import platform

TIMEDELTA_RENEWAL_WINDOW = 120

class UPNP_HEADERS:
    USER_AGENT = "AutomationMojo/1.0 UPNP Test Package"
    SERVER = "{},{},AutomationKit/1.0".format(platform.system(), platform.release())
