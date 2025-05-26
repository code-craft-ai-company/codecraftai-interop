
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


def xml_format_service_desc(
    serviceType: str,
    serviceId: str,
    controlURL: str,
    eventSubURL: str,
    SCPDURL: str,
    indent: str = ""
) -> str:
    """
    Create an XML representation of a service description.

    :param service_type: Type of the service.
    :param service_id: ID of the service.
    :param control_url: Control URL of the service.
    :param event_sub_url: Event subscription URL of the service.
    :param scpd_url: SCPD URL of the service.
    :param indent: Indentation for the XML string.
    :returns: XML string representation of the service description.
    """
    
    desc_lines = [
        f"{indent}<service>",
        f"{indent}    <serviceType>{serviceType}</serviceType>",
        f"{indent}    <serviceId>{serviceId}</serviceId>",
        f"{indent}    <controlURL>{controlURL}</controlURL>",
        f"{indent}    <eventSubURL>{eventSubURL}</eventSubURL>",
        f"{indent}    <SCPDURL>{SCPDURL}</SCPDURL>",
        f"{indent}</service>"
    ]

    desc = "\r\n".join(desc_lines)

    return desc


class ServiceDesc:
    """
        Class representing a UPnP service description.
    """

    def __init__(self, *, serviceType: str, serviceId: str, controlURL: str, eventSubURL: str, SCPDURL: str):
        self.serviceType = serviceType
        self.serviceId = serviceId
        self.controlURL = controlURL
        self.eventSubURL = eventSubURL
        self.SCPDURL = SCPDURL
        return
    
    def as_dict(self) -> dict:
        """
        Convert the ServiceDesc object to a dictionary.

        :returns: Dictionary representation of the ServiceDesc object.
        """
        
        desc = {
            "serviceType": self.serviceType,
            "serviceId": self.serviceId,
            "controlURL": self.controlURL,
            "eventSubURL": self.eventSubURL,
            "SCPDURL": self.SCPDURL
        }

        return desc 
    
    def as_xml(self, indent="") -> str:
        """
        Convert the ServiceDesc object to an XML string.

        :param indent: Indentation for the XML string.

        :returns: XML string representation of the ServiceDesc object.
        """
        
        desc = xml_format_service_desc(
            serviceType=self.serviceType,
            serviceId=self.serviceId,
            controlURL=self.controlURL,
            eventSubURL=self.eventSubURL,
            SCPDURL=self.SCPDURL,
            indent=indent
        )

        return desc
    
    def generate_extension_key(self) -> str:
        """
            Generates a unique key that identifies an extension type based on where
            it was found in a hiearchy of code containers.

            :returns: A unique path like string that is an identifier used to lookup a device type.
        """
        extkey = f"{self.serviceType}/{self.serviceId}"
        return extkey

    def __repr__(self):
        rval = f"ServiceDesc(serviceType={self.serviceType}, serviceId={self.serviceId})"
        return rval

