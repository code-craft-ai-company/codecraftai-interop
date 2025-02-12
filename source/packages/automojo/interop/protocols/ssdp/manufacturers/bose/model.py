
"""
.. module:: model
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing data description classes that describe Bose UPNP devices.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Dict, List, Union

from automojo.interop.protocols.ssdp.model import (
    DeviceDetail,
    EmbeddedDeviceInfo,
    IconInfo,
    ServiceInfo
)


"""
    <bose:X_MAC>ACBF7199AB83</bose:X_MAC>
<bose:X_ecoSystem>ECO2</bose:X_ecoSystem>
<bose:X_productType>taylor</bose:X_productType>
<bose:X_productColor>1</bose:X_productColor>
<bose:X_softwareVersion>20.0.11-231aae5</bose:X_softwareVersion>
<bose:X_multiroomVersions>
    <NowPlaying_Version>
        <major_version>1</major_version>
        <minor_version>0</minor_version>
    </NowPlaying_Version>
    <PlaybackRequest_Version>
        <major_version>1</major_version>
        <minor_version>0</minor_version>
    </PlaybackRequest_Version>
    <ZoneControl_Version>
        <major_version/>
        <minor_version/>
    </ZoneControl_Version>
    <Audio_Payload_Version>
        <major_version>1</major_version>
        <minor_version>0</minor_version>
    </Audio_Payload_Version>
    <AudioControl_Protocol_Version>
        <major_version>2</major_version>
        <minor_version>0</minor_version>
    </AudioControl_Protocol_Version>
    <ClockSync_Protocol_Version>
        <major_version>2</major_version>
        <minor_version>1</minor_version>
    </ClockSync_Protocol_Version>
</bose:X_multiroomVersions>
"""

class BoseFeatureVersion:

    def __init__(self, major: int, minor: int):
        self._major = major
        self._minor = minor
        return

class BoseMultiRoomVersions:

    def __init__(self, audio_control: BoseFeatureVersion, audio_payload: BoseFeatureVersion, clock_sync: BoseFeatureVersion,
                 now_playing: BoseFeatureVersion, playback_request: BoseFeatureVersion, zone_control: BoseFeatureVersion):
        self._audio_control = audio_control
        self._audio_payload = audio_payload
        self._clock_sync = clock_sync
        self._now_playing = now_playing
        self._playback_request = playback_request
        self._zone_control = zone_control
        return

    @property
    def audio_control(self) -> BoseFeatureVersion:
        return self._audio_control
    
    @property
    def audio_payload(self) -> BoseFeatureVersion:
        return self._audio_payload
    
    @property
    def clock_sync(self) -> BoseFeatureVersion:
        return self._clock_sync
    
    @property
    def now_playing(self) -> BoseFeatureVersion:
        return self._now_playing
    
    @property
    def playback_request(self) -> BoseFeatureVersion:
        return self._playback_request
    
    @property
    def zone_control(self) -> BoseFeatureVersion:
        return self._zone_control


class BoseDeviceDetail(DeviceDetail):

    def __init__(self, *, deviceType: str, friendlyName: str, manufacturer: str, manufacturerURL: Union[str, None], modelDescription: Union[str, None],
                 modelName: str, modelNumber: Union[str, None], modelURL: Union[str, None], presentationURL: str, UDN: str, iconList: List[IconInfo],
                 serialNumber: Union[str, None], serviceList: List[ServiceInfo], deviceList: List[EmbeddedDeviceInfo], UPC: Union[str, None],
                 mac_addr: str, generation: str, codename: str, color: str, software_version: str, multi_room: BoseMultiRoomVersions, extra: Dict[str, str]):
        super().__init__(deviceType=deviceType, friendlyName=friendlyName, manufacturer=manufacturer, manufacturerURL=manufacturerURL,
                         modelDescription=modelDescription, modelName=modelName, modelNumber=modelNumber, modelURL=modelURL, presentationURL=presentationURL,
                         UDN=UDN, iconList=iconList, serialNumber=serialNumber, serviceList=serviceList, deviceList=deviceList, UPC=UPC,
                         mac_addr=mac_addr, generation=generation, codename=codename, color=color, software_version=software_version, extra=extra)
        
        
        self._multiroom = multi_room

        return

    @property
    def multiroom(self) -> BoseMultiRoomVersions:
        return self._multiroom
