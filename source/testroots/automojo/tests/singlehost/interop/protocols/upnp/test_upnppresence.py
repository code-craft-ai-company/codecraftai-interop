import automojo.testbase as testbase

from automojo.interop.protocols.upnp.upnppresence import UpnpPresence
from automojo.interop.protocols.upnp.model.description.deviceevidence import DeviceEvidence


def _create_evidence(presence: UpnpPresence, usn: str, status: str) -> DeviceEvidence:
    return DeviceEvidence(
        usn=usn,
        status=status,
        server="server",
        location="loc",
        ip="1.1.1.1",
        other={},
        presence=presence,
    )


def test_active_and_inactive_device_types() -> None:
    presence = UpnpPresence()

    active = _create_evidence(presence, "usn1", "active")
    inactive = _create_evidence(presence, "usn2", "inactive")

    presence._active_devices["usn1"] = active
    presence._inactive_devices["usn2"] = inactive

    actives = presence.active_devices
    inactives = presence.inactive_devices

    testbase.assert_equal(all(isinstance(v, DeviceEvidence) for v in actives.values()), True)
    testbase.assert_equal(all(isinstance(v, DeviceEvidence) for v in inactives.values()), True)
    return

