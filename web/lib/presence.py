from typing import Optional
import time
import logging

from lib.cache import REDIS

from channels_presence.models import Room
from channels_presence.models import Presence

from . import channels
from . import cache


def broadcast_ws_connection_change(group_name: str) -> None:
    (group, printer_id_str) = group_name.split('.')
    printer_id = int(printer_id_str)
    if group == 'p_web':
        channels.send_msg_to_printer(
            printer_id,
            {'remote_status': {'viewing': presence.get_group_size(group_name) > 0}})
    if group == 'p_octo':
        if presence.get_group_size(group_name) <= 0:
            cache.printer_status_delete(printer_id)
        channels.send_status_to_web(printer_id)


class RedisPresence:
    EXPIRATION_SECS = {
        "p_octo": 120,
        "p_web": 120,
        "_default": 1200,
    }

    def add_to_group(self, group_name: str, channel_name: str, cur_time: Optional[float] = None) -> None:
        t = cur_time if cur_time is not None else time.time()
        key = self._get_prefixed_group_name(group_name)
        exp = self._get_expiration_for_group_name(group_name)
        with REDIS.pipeline() as conn:
            # removing expired groups here
            conn.zremrangebyscore(key, min="-inf", max=t - exp)

            conn.zadd(key, {channel_name: t})
            conn.expire(key, exp)
            ret = conn.execute()

            if ret and ret[0]:
                logging.debug(f"dropped {ret[0]} expired connections from presence group {group_name}")

        broadcast_ws_connection_change(group_name)

    def remove_from_group(self, group_name: str, channel_name: str) -> None:
        key = self._get_prefixed_group_name(group_name)
        REDIS.zrem(key, channel_name)

        broadcast_ws_connection_change(group_name)

    def touch(self, group_name: str, channel_name: str, cur_time: Optional[float] = None) -> None:
        t = cur_time if cur_time is not None else time.time()
        key = self._get_prefixed_group_name(group_name)
        exp = self._get_expiration_for_group_name(group_name)
        with REDIS.pipeline() as conn:
            conn.zadd(key, {channel_name: t})
            conn.expire(key, exp)
            conn.execute()

    def get_group_size(self, group_name: str, cur_time: Optional[float] = None) -> int:
        t = cur_time if cur_time is not None else time.time()
        exp = self._get_expiration_for_group_name(group_name)
        key = self._get_prefixed_group_name(group_name)
        return len(REDIS.zrangebyscore(key, min=t - exp, max="+inf"))

    def _get_expiration_for_group_name(self, group_name: str) -> None:
        group = group_name.split(".")[0]
        return self.EXPIRATION_SECS.get(
            group,
            self.EXPIRATION_SECS["_default"])

    def _get_prefixed_group_name(self, group_name: str) -> str:
        return f"presence:group:{group_name}"


presence = RedisPresence()
