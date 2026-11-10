"""Optional DNS recovery for the demo process; TLS still verifies the original host."""
from __future__ import annotations

import ipaddress
import socket
import time

import requests


def enable_gateway_dns_fallback() -> None:
    """Use public DNS over HTTPS only if system DNS fails for the CKEY gateway.

    No hosts file, adapter settings, API endpoint, headers or TLS settings change.
    Cached answers expire after at most five minutes. Other hosts use system DNS.
    """
    original = socket.getaddrinfo
    cached: dict[str, object] = {}

    def resolve(host, port, *args, **kwargs):
        if host not in ("api.xah.io", b"api.xah.io"):
            return original(host, port, *args, **kwargs)
        if cached.get("expires", 0) > time.monotonic():
            return original(cached["ip"], port, *args, **kwargs)
        try:
            return original(host, port, *args, **kwargs)
        except socket.gaierror:
            response = requests.get("https://dns.google/resolve",
                                    params={"name": "api.xah.io", "type": "A"}, timeout=10)
            response.raise_for_status()
            data = response.json()
            answers = [a for a in data.get("Answer", []) if a.get("type") == 1]
            if data.get("Status") != 0 or not answers:
                raise socket.gaierror("Gateway DNS lookup did not return an IPv4 address")
            address = str(ipaddress.IPv4Address(answers[0]["data"]))
            cached.update(ip=address, expires=time.monotonic() + min(300, max(1, int(answers[0].get("TTL", 60)))))
            return original(address, port, *args, **kwargs)

    socket.getaddrinfo = resolve
