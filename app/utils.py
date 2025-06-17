import ipaddress
import re
from typing import Optional


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
    
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def sanitize_ip_address(ip: str) -> Optional[str]:
    """
    Sanitize and validate IP address string.
    
    Args:
        ip: IP address string to sanitize
        
    Returns:
        str: Sanitized IP address or None if invalid
    """
    if not ip:
        return None
    
    # Remove whitespace and convert to string
    ip = str(ip).strip()
    
    # Basic format check
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        return None
    
    # Validate with ipaddress module
    try:
        ip_obj = ipaddress.ip_address(ip)
        return str(ip_obj)
    except ValueError:
        return None


def is_private_ip(ip: str) -> bool:
    """
    Check if the given IP address is private.
    
    Args:
        ip: IP address string to check
        
    Returns:
        bool: True if private IP, False otherwise
    """
    if not validate_ip_address(ip):
        return False
    
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


def format_error_message(error: Exception) -> str:
    """
    Format error message for logging and user display.
    
    Args:
        error: Exception object
        
    Returns:
        str: Formatted error message
    """
    return f"{type(error).__name__}: {str(error)}" 