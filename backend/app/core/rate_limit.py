from fastapi import Request
from slowapi.util import get_remote_address


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        client_ip = forwarded_for.split(",", 1)[0].strip()
        if client_ip:
            return client_ip

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    return get_remote_address(request)
