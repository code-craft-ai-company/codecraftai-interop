
import os

from xml.etree.ElementTree import fromstring as parse_xml_content

from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger

from automojo.interop.protocols.upnp.constants import UPNP_DEVICE1_NAMESPACE


from automojo.interop.protocols.upnp.mapping.devicedetailmapper import DeviceDetailMapper
from automojo.interop.protocols.upnp.model.description.basic1devicedesc import Basic1DeviceDesc
from automojo.interop.protocols.upnp.model.description.servicedesc import ServiceDesc
from automojo.interop.protocols.upnp.model.description.serviceevidence import ServiceEvidence

from automojo.interop.protocols.upnp.generation.common import (
    parse_service_type
)

from automojo.interop.protocols.upnp.wellknown import DeviceDetailMapperRegistrySingleton

logger = getEnhancedLogger()

class DeviceCacheManager:

    def __init__(self, device_cache_root: str, service_cache_root: str):
        self._device_cache_root = device_cache_root
        self._service_cache_root = service_cache_root
        
        self._device_static_root = ""
        self._service_static_root = ""

        self._mapper_registry = DeviceDetailMapperRegistrySingleton()
        return


    def load_device_description(self, device_cache_leaf: str) -> Basic1DeviceDesc:
        """
            Load a UPnP device description from an xml description file.

            :param device_cache_leaf: Leaf path of the device description file to load.

            :returns: Parsed :class:`Basic1DeviceDesc`.
        """

        device_desc = None

        desc_filename = os.path.join(self._device_cache_root, device_cache_leaf)

        with open(desc_filename, 'r') as ddf:
            desc_content = ddf.read()

            try:
                default_namespaces = {"": UPNP_DEVICE1_NAMESPACE}
                root_el = parse_xml_content(desc_content)
                
                spec_ver, manufacturer = DeviceDetailMapper.pull_spec_version_and_manufacturer(root_el, default_namespaces)
                
                if spec_ver is not None and manufacturer is not None:

                    mapper = self._mapper_registry.lookup_device_detail_mapper(manufacturer)
                    
                    device_desc = mapper.create_root_device_description(root_el, default_namespaces, spec_ver, locationURL=desc_filename)
                
            except Exception as parse_err:
                err_msg = f"Error parsing device description XML: {parse_err}"
                logger.error(err_msg)


        return device_desc
    

    def load_service_description(self, service_evidence: ServiceEvidence) -> ServiceDesc:
        """
            Load a service description from the device service cache.

            :raises: FileNotFound error and XML Parse Errors
        """
        service_type = service_evidence.serviceType

        parse_service_type(service_type)

        service_agency, service_name = parse_service_type(service_type)

        service_agency = service_agency.lower()
        service_name = service_name.lower()

        service_dir = os.path.join(self._service_cache_root, service_agency)
        if not os.path.exists(service_dir):
            os.makedirs(service_dir)

        service_desc_filename = os.path.join(service_dir, f"{service_name}.xml")

        desc_content = ServiceDesc.load_service_description(service_desc_filename)

        return desc_content