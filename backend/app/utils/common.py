from typing import List, Optional
from datetime import datetime
import re
import ipaddress
from typing import Optional


def parse_ip_list(value) -> List[str]:
    """Parse IP field into a list of strings."""
    if isinstance(value, list):
        return [v for v in value if v]
    if isinstance(value, str) and value and value != "[]":
        return [value]
    return []


def parse_single_ip(value) -> Optional[str]:
    """Parse IP field into a single string."""
    if isinstance(value, list) and value:
        return value[0]
    if isinstance(value, str) and value and value != "[]":
        return value
    return None


def parse_time(t_str: Optional[str]) -> datetime:
    """Parse timestamp string to datetime."""
    if not t_str:
        return datetime.utcnow()
    try:
        return datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.utcnow()


def is_valid_ip(ip: str) -> bool:
    """Validate IP address (IPv4/IPv6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_domain(domain: str) -> bool:
    """Validate domain name."""
    if not domain or len(domain) > 255:
        return False
    # Simple regex for domain validation
    pattern = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
    )
    return bool(pattern.match(domain))


def is_valid_url(url: str) -> bool:
    """Validate URL."""
    # Basic URL check
    return url.startswith(("http://", "https://"))


def is_valid_hash(hash_val: str) -> bool:
    """Validate MD5/SHA1/SHA256 hash."""
    length = len(hash_val)
    if length not in (32, 40, 64):
        return False
    return bool(re.match(r"^[a-fA-F0-9]+$", hash_val))


def is_valid_email(email: str) -> bool:
    """Validate email address."""
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(pattern.match(email))
