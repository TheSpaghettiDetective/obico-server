"""Whether a host name points only at the public internet.

The server sends notifications to addresses that users type in. Those must never
reach the server's own machine or network, such as the cloud metadata address,
Redis, or a private, shared (100.64.0.0/10) or link-local range.
"""
import ipaddress
import socket
from typing import Optional


def is_public_host(host: str) -> Optional[bool]:
    """True when every address `host` stands for is a public internet address,
    False when any is not, and None when `host` is not an address and does not
    resolve."""
    host = (host or '').strip('[]')
    try:
        addrs = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, None)
        except (socket.gaierror, UnicodeError):
            return None
        addrs = [ipaddress.ip_address(info[4][0].split('%')[0]) for info in infos]
    for addr in addrs:
        if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
            addr = addr.ipv4_mapped
        if not addr.is_global or addr.is_multicast:
            return False
    return bool(addrs)
