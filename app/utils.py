import ipaddress
from typing import Optional

from flask import Request


def validate_ip_address(ip: str) -> bool:
    """
    Validate if the given string is a valid IP address.

    Args:
        ip: IP address string to validate

    Returns:
        bool: True if valid IP address, False otherwise
    """
    if not ip or not isinstance(ip, str):
        return False
    # Validate with ipaddress module
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_real_ip(request: Request, depth: int = 0) -> Optional[str]:
    """
    Get the real client IP address from the request.

    Args:
        request: Flask request object
        depth: Recursion depth for proxy headers

    Returns:
        str: Real client IP address or None if not found
    """

    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        # Strip whitespace and split by comma
        ips = [ip.strip() for ip in xff.split(",")]
        if len(ips) > depth:
            return ips[depth]
        else:
            return ips[0]
    # Fallback last to remote_addr
    return request.remote_addr
