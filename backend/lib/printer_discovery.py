import dataclasses
import json
import time
import re
import random
import string

from rest_framework import serializers
from typing import Optional, List
from ipware.utils import (
    cleanup_ip, is_valid_ip, is_public_ip)

from lib.cache import (
    disco_push_raw_device_message,
    disco_pop_raw_device_messages,
    disco_update_raw_device_info,
    disco_get_active_raw_device_infos,
    disco_existed_one_time_passcode,
    disco_create_one_time_passcode,
)

# message to device will expire in ..
LINKHELPER_MESSAGE_EXPIRATION_SECS = 60

# device is considered offline if does not call in ..
LINKHELPER_PRESENCE_EXPIRATION_SECS = 4


class DeviceInfoSerializer(serializers.Serializer):
    device_id = serializers.CharField(
        required=True, min_length=32, max_length=32)
    hostname = serializers.CharField(
        required=True, max_length=253)
    os = serializers.CharField(
        required=True, max_length=253, allow_blank=True)
    arch = serializers.CharField(
        required=True, max_length=253, allow_blank=True)
    rpi_model = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')
    octopi_version = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')
    printerprofile = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')
    machine_type = serializers.CharField(
        required=True, max_length=253, allow_blank=True)
    host_or_ip = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')
    port = serializers.IntegerField(
        required=False, min_value=1, max_value=65535,
        allow_null=True, default=None)
    plugin_version = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')
    agent = serializers.CharField(
        required=False, max_length=253, allow_blank=True, default='')

    def validate_host_or_ip(self, value):
        if value:
            ip = cleanup_ip(value)
            if is_valid_ip(ip) and not is_public_ip(ip):
                return ip
            raise serializers.ValidationError('Must be private ip address')
        return value


class DeviceMessageSerializer(serializers.Serializer):
    device_id = serializers.CharField(
        required=True, min_length=32, max_length=32)
    type = serializers.CharField(required=True, max_length=64)
    data = serializers.DictField(required=True)  # type: ignore


@dataclasses.dataclass
class DeviceInfo:
    device_id: str
    hostname: str
    os: str
    arch: str
    octopi_version: Optional[str]
    rpi_model: str
    printerprofile: Optional[str]
    machine_type: str
    host_or_ip: str
    port: Optional[int]
    plugin_version: Optional[str]
    agent: Optional[str]

    @classmethod
    def from_dict(cls, data) -> 'DeviceInfo':
        serializer = DeviceInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        return DeviceInfo(**{k: v for (k, v) in validated.items()})

    @classmethod
    def from_json(cls, raw: str) -> 'DeviceInfo':
        return DeviceInfo.from_dict(json.loads(raw))

    def to_json(self) -> str:
        return json.dumps(self.asdict())

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class DeviceMessage:
    device_id: str
    type: str
    data: dict

    @classmethod
    def from_dict(cls, data) -> 'DeviceMessage':
        serializer = DeviceMessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        return DeviceMessage(**{k: v for (k, v) in validated.items()})

    @classmethod
    def from_json(cls, raw: str) -> 'DeviceMessage':
        return DeviceMessage.from_dict(json.loads(raw))

    def to_json(self) -> str:
        return json.dumps(self.asdict())

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


def push_message_for_device(
    client_ip: str,
    device_id: str,
    message: DeviceMessage,
    cur_time: Optional[float] = None,
    expiration_secs: int = LINKHELPER_MESSAGE_EXPIRATION_SECS
) -> None:
    t = cur_time if cur_time is not None else time.time()
    raw = message.to_json()
    disco_push_raw_device_message(
        client_ip=client_ip,
        device_id=device_id,
        raw_message=raw,
        cur_time=t,
        expiration_secs=expiration_secs
    )


def pull_messages_for_device(
    client_ip: str,
    device_id: str,
    message_count: int = 3,
    cur_time: Optional[float] = None,
    expiration_secs: int = LINKHELPER_MESSAGE_EXPIRATION_SECS
) -> List[DeviceMessage]:
    t = cur_time if cur_time is not None else time.time()

    raw_messages = disco_pop_raw_device_messages(
        client_ip=client_ip,
        device_id=device_id,
        cur_time=t,
        expiration_secs=expiration_secs,
        message_count=message_count,
    )

    messages = []
    for raw in raw_messages:
        msg = DeviceMessage.from_json(raw)
        if msg is not None:
            messages.append(msg)
    return messages


def get_active_devices_for_client_ip(
    client_ip: str,
    cur_time: Optional[float] = None,
    expiration_secs: int = LINKHELPER_PRESENCE_EXPIRATION_SECS,
) -> List[DeviceInfo]:
    t = cur_time if cur_time is not None else time.time()

    raw_deviceinfos = disco_get_active_raw_device_infos(
        client_ip=client_ip,
        cur_time=t,
        expiration_secs=expiration_secs,
    )

    dinfos = []
    for device_info_raw in raw_deviceinfos:
        # might have expired in the meantime, skip it
        if not device_info_raw:
            continue

        dinfo = DeviceInfo.from_json(device_info_raw)
        if dinfo is not None:
            dinfos.append(dinfo)
    return dinfos


def update_presence_for_device(
    client_ip: str,
    device_id: str,
    device_info: DeviceInfo,
    cur_time: Optional[float] = None,
    expiration_secs: int = LINKHELPER_PRESENCE_EXPIRATION_SECS,

) -> None:
    t = cur_time if cur_time is not None else time.time()
    raw = device_info.to_json()
    return disco_update_raw_device_info(
        client_ip=client_ip,
        device_id=device_id,
        raw_deviceinfo=raw,
        cur_time=t,
        expiration_secs=expiration_secs)


def disco_get_or_create_one_time_passcode(old_code: str, code_length=5) -> str:
    if disco_existed_one_time_passcode(old_code):
        return old_code
    else:
        letters_and_digits = string.ascii_letters + string.digits
        new_code = ''.join(random.choice(letters_and_digits) for _ in range(code_length)).upper()
        disco_create_one_time_passcode(new_code)
        return new_code
