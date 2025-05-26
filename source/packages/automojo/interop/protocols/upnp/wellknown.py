

import threading

from automojo.interop.protocols.upnp.mapping.devicedetailmapperregistry import DeviceDetailMapperRegistry

_lock = threading.Lock()

DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON = None

def DeviceDetailMapperRegistrySingleton() -> DeviceDetailMapperRegistry:
    """
        Singleton for the device detail mapper registry.
    """
    global DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON

    if DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON is None:
        with _lock:
            if DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON is None:
                DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON = DeviceDetailMapperRegistry()

    return DEVICE_DETAIL_MAPPER_REGISTRY_SINGLETON
