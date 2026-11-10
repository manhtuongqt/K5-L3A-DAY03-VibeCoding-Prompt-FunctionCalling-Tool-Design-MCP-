import socket

from conftest import FakeResponse
from demo_dns import enable_gateway_dns_fallback


def test_working_system_dns_does_not_use_fallback(monkeypatch):
    calls = []
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, *args, **kwargs: calls.append(host) or ["system"])
    enable_gateway_dns_fallback()
    assert socket.getaddrinfo("api.xah.io", 443) == ["system"]
    assert calls == ["api.xah.io"]


def test_failed_gateway_dns_uses_cached_address_only_for_gateway(monkeypatch, fake_http):
    calls = []
    def system(host, *args, **kwargs):
        calls.append(host)
        if host == "api.xah.io":
            raise socket.gaierror("DNS unavailable")
        return [host]
    monkeypatch.setattr(socket, "getaddrinfo", system)
    requests = fake_http(FakeResponse({"Status": 0, "Answer": [{"type": 1, "data": "203.0.113.1", "TTL": 300}]}))
    enable_gateway_dns_fallback()
    assert socket.getaddrinfo("api.xah.io", 443) == ["203.0.113.1"]
    assert socket.getaddrinfo("api.xah.io", 443) == ["203.0.113.1"]
    assert socket.getaddrinfo("example.com", 443) == ["example.com"]
    assert calls.count("api.xah.io") == 1
    assert len(requests) == 1
    assert "headers" not in requests[0]
