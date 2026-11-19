import dataclasses
import hashlib
import hmac
import json
import time
import re
import random
import string

from rest_framework import serializers
from typing import Optional, List

from lib.cache import (
    disco_push_raw_device_message,
    disco_pop_raw_device_messages,
    disco_update_raw_device_info,
    disco_get_active_raw_device_infos,
    disco_claim_device_secret_hash,
    disco_get_device_secret_hash,
)

# message to device will expire in ..
LINKHELPER_MESSAGE_EXPIRATION_SECS = 60

# device is considered offline if does not call in ..
LINKHELPER_PRESENCE_EXPIRATION_SECS = 4

# a device's secret hash is kept this long after its last announcement
LINKHELPER_SECRET_HASH_EXPIRATION_SECS = 60 * 60


class DeviceMessageSerializer(serializers.Serializer):
    device_id = serializers.CharField(
        required=True, min_length=32, max_length=32)
    type = serializers.CharField(required=True, max_length=64)
    data = serializers.DictField(required=True)  # type: ignore


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
):
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

        dinfo = json.loads(device_info_raw)
        if dinfo is not None:
            dinfos.append(dinfo)

    return dinfos


def update_presence_for_device(
    client_ip: str,
    device_id: str,
    device_info: dict,
    cur_time: Optional[float] = None,
    expiration_secs: int = LINKHELPER_PRESENCE_EXPIRATION_SECS,

) -> None:
    t = cur_time if cur_time is not None else time.time()
    return disco_update_raw_device_info(
        client_ip=client_ip,
        device_id=device_id,
        raw_deviceinfo=json.dumps(device_info),
        cur_time=t,
        expiration_secs=expiration_secs)


def hash_device_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def is_announced_by_device(client_ip: str, device_id: str, secret_hash: Optional[str]) -> bool:
    # Whether an announcement comes from the device that first announced this device_id.
    # Anyone behind the same address can see a device_id and announce it too. A device whose
    # first announcement carries the hash of its secret is told apart from them. One whose first
    # announcement carries no hash (plugins released before the hash was added) is not, as before.
    stored = disco_claim_device_secret_hash(
        client_ip=client_ip,
        device_id=device_id,
        secret_hash=secret_hash,
        expiration_secs=LINKHELPER_SECRET_HASH_EXPIRATION_SECS,
    )
    return not stored or (secret_hash is not None and hmac.compare_digest(stored, secret_hash))


def is_secret_of_device(client_ip: str, device_id: str, secret: str) -> bool:
    stored = disco_get_device_secret_hash(client_ip, device_id)
    return not stored or hmac.compare_digest(stored, hash_device_secret(secret))
