
from typing import List

import os
import sys

import requests

from automojo.presence.wellknown import ConfiguredSuperFactorySingleton

from automojo.interop.protocols.upnp.generation.common import (
    normalize_model_name,
    parse_service_type
)

from automojo.interop.protocols.upnp.upnppresence import UpnpPresence
from automojo.interop.protocols.upnp.model.description.basic1devicedesc import Basic1DeviceDesc
from automojo.interop.protocols.upnp.model.description.serviceevidence import ServiceEvidence

from automojo.runtime.runtimevariables import AM_RUNTIME_VARIABLES


def pull_device_description(device_scan_directory: str, device_name: str, device_desc: Basic1DeviceDesc):

    device_ext_dir = os.path.join(device_scan_directory, device_desc.manufacturer)
    if not os.path.exists(device_ext_dir):
        os.makedirs(device_ext_dir)

    device_desc_file = os.path.join(device_ext_dir, f"{device_name}.xml")
    
    location_url = device_desc.locationURL

    resp: requests.Response = requests.get(location_url)
    if resp.status_code == 200:
        desc_content = resp.content.decode("utf-8")
        with open(device_desc_file, 'w+') as ddf:
            ddf.write(desc_content)
    
    return

def pull_service_description(service_scan_directory: str, device_desc: Basic1DeviceDesc, service_evidence: ServiceEvidence):
    """
    """
    service_type = service_evidence.serviceType

    service_agency, service_name = parse_service_type(service_type)

    service_dir = os.path.join(service_scan_directory, service_agency)
    if not os.path.exists(service_dir):
        os.makedirs(service_dir)

    service_desc_filename = os.path.join(service_dir, f"{service_name.lower()}.xml")

    if not os.path.exists(service_desc_filename):
        base_url = device_desc.baseURL.rstrip("/")
        service_desc_url = f"{base_url}/{service_evidence.SCPDURL.lstrip('/')}"

        resp: requests.Response = requests.get(service_desc_url)
        if resp.status_code == 200:
            desc_content = resp.content.decode("utf-8")
            with open(service_desc_filename, 'w+') as sdf:
                sdf.write(desc_content)

    return

def upnp_scan_devices(window_length: float, factory_modules: List[str]):

    super_factory = ConfiguredSuperFactorySingleton()

    for fmod in factory_modules:
        super_factory.add_factory_module(fmod)
    
    scanner = UpnpPresence()
    
    scanner.start()
    
    # Perform a discovery
    print("")
    print("---------- STARTING DISCOVERY ----------")
    disco_window = scanner.discover_devices(window_length=window_length)
    disco_window.wait()

    device_scan_directory = os.path.join(AM_RUNTIME_VARIABLES.AM_PRESENCE_DIRECTORY, "scan", "upnp", "devices")
    if not os.path.exists(device_scan_directory):
        os.makedirs(device_scan_directory)
    
    service_scan_directory = os.path.join(AM_RUNTIME_VARIABLES.AM_PRESENCE_DIRECTORY, "scan", "upnp", "services")
    if not os.path.exists(service_scan_directory):
        os.makedirs(service_scan_directory)

    print("")
    print("------------ PROCESSING DEVICES AND SERVICES -------------")
    for usn, device in disco_window.devices_found.items():
        device_evidence = device.evidence
        device_desc = device.description

        device_name = normalize_model_name(device_desc.modelName)
        print(f"Processing Device: {usn} ({type(device_desc).__name__})")
        print(f"  Location: {device_evidence.location}")
        print(f"  Model: {device_desc.modelName}")
        print(f"  Manufacturer: {device_desc.manufacturer}")
        print(f"  Serial Number: {device_desc.serialNumber}")
        print("")

        pull_device_description(device_scan_directory, device_name, device_desc)

        for service_evidence in device_desc.serviceList:
            pull_service_description(service_scan_directory, device_desc, service_evidence)

    return

def upnp_scan_devices_main():

    """
        Debug the  UPnP discovery process.
    """

    window_length = 30.0
    factory_modules = [
        "automojo.interop.manufacturers.bose.boseupnpextension"
    ]

    upnp_scan_devices(window_length=window_length, factory_modules=factory_modules)
    
    return


if __name__ == "__main__":
    upnp_scan_devices_main()

