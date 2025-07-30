from typing import List

class UpnpDeviceClassGenerator:

    MANUFACTURER = None
    
    @classmethod
    def get_base_device_imports(cls) -> List[str]:
        raise NotImplementedError(f"'get_base_device_imports' must be implemented by the '{cls.__name__}' extensions.")

    @classmethod
    def get_base_device_type_name(cls) -> str:

        raise NotImplementedError(f"'get_base_device_type_name' must be implemented by the '{cls.__name__}' extensions.")

    @classmethod
    def generate_device_class(description: str) -> None:

        return