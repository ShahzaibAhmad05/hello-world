import string
import random
import validators
from typing import Optional
from urllib.parse import urlparse

# Base62 alphabet for URL encoding
BASE62_ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length: int = 6) -> str:
    """Generate a random short code using base62 characters"""
    return ''.join(random.choices(BASE62_ALPHABET, k=length))

def encode_id(id_num: int) -> str:
    """Encode an integer ID to base62 string"""
    if id_num == 0:
        return BASE62_ALPHABET[0]
    
    result = []
    base = len(BASE62_ALPHABET)
    
    while id_num:
        id_num, remainder = divmod(id_num, base)
        result.append(BASE62_ALPHABET[remainder])
    
    return ''.join(reversed(result))

def decode_short_code(short_code: str) -> int:
    """Decode a base62 string to integer ID"""
    result = 0
    base = len(BASE62_ALPHABET)
    
    for char in short_code:
        result = result * base + BASE62_ALPHABET.index(char)
    
    return result

def validate_url(url: str) -> bool:
    """Validate if a URL is properly formatted"""
    if not url or len(url.strip()) == 0:
        return False
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Use validators library for comprehensive validation
    return validators.url(url)

def normalize_url(url: str) -> str:
    """Normalize URL by adding protocol if missing and validating"""
    if not url or len(url.strip()) == 0:
        raise ValueError("URL cannot be empty")
    
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validate the URL
    if not validators.url(url):
        raise ValueError("Invalid URL format")
    
    return url

def is_safe_url(url: str) -> bool:
    """Check if URL is safe (not pointing to localhost or internal IPs)"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Block localhost and common internal addresses
        blocked_hosts = {'localhost', '127.0.0.1', '::1', '0.0.0.0'}
        if hostname.lower() in blocked_hosts:
            return False
        
        # Block private IP ranges (basic check)
        if hostname.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.')):
            return False
        
        return True
    except Exception:
        return False

def get_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None