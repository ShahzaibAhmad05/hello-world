"""
Caching Layer for User Storage
Implements cache-aside pattern with TTL and LRU eviction
"""

import time
from typing import Dict, Optional, Any
from threading import Lock
from collections import OrderedDict


class CacheEntry:
    """Represents a cached entry with TTL"""
    
    def __init__(self, value: Any, ttl: int):
        """
        Initialize cache entry
        
        Args:
            value: The cached value
            ttl: Time-to-live in seconds
        """
        self.value = value
        self.expiry = time.time() + ttl if ttl > 0 else float('inf')
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() > self.expiry


class LRUCache:
    """
    LRU (Least Recently Used) Cache with TTL support
    Thread-safe implementation for concurrent access
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of entries (default: 1000)
            default_ttl: Default time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = Lock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiry
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self.lock:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove if exists (to update position)
            if key in self.cache:
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = CacheEntry(value, ttl)
            
            # Evict LRU if over max size
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)  # Remove oldest
                self.evictions += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': round(hit_rate, 2)
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)


class CachedUserStore:
    """
    Cached wrapper for user storage
    Implements cache-aside pattern with automatic invalidation
    """
    
    def __init__(self, user_store, cache_size: int = 1000, ttl: int = 300):
        """
        Initialize cached user store
        
        Args:
            user_store: Underlying user storage instance
            cache_size: Maximum cache size (default: 1000)
            ttl: Cache TTL in seconds (default: 300 = 5 minutes)
        """
        self.user_store = user_store
        self.cache = LRUCache(max_size=cache_size, default_ttl=ttl)
    
    def _email_key(self, email: str) -> str:
        """Generate cache key for email lookup"""
        return f"email:{email.lower()}"
    
    def _id_key(self, user_id: str) -> str:
        """Generate cache key for ID lookup"""
        return f"id:{user_id}"
    
    def _duplicate_key(self, email: str) -> str:
        """Generate cache key for duplicate check"""
        return f"dup:{email.lower()}"
    
    def check_duplicate(self, email: str) -> bool:
        """
        Check if email exists (cached)
        
        Args:
            email: Email address
        
        Returns:
            True if exists, False otherwise
        """
        cache_key = self._duplicate_key(email)
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - check underlying store
        result = self.user_store.check_duplicate(email)
        
        # Cache the result
        self.cache.set(cache_key, result)
        
        return result
    
    def save_user(self, user_data: Dict) -> bool:
        """
        Save user and invalidate related cache entries
        
        Args:
            user_data: User data dictionary
        
        Returns:
            True if successful
        """
        email = user_data['email'].lower()
        user_id = user_data['user_id']
        
        # Save to underlying store
        success = self.user_store.save_user(user_data)
        
        if success:
            # Invalidate related cache entries
            self._invalidate_user_cache(email, user_id)
            
            # Cache the new user data
            self.cache.set(self._email_key(email), user_data)
            self.cache.set(self._id_key(user_id), user_data)
            self.cache.set(self._duplicate_key(email), True)
        
        return success
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email (cached)
        
        Args:
            email: Email address
        
        Returns:
            User data or None
        """
        cache_key = self._email_key(email)
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - get from underlying store
        user_data = self.user_store.get_user_by_email(email)
        
        # Cache the result if found
        if user_data:
            self.cache.set(cache_key, user_data)
            # Also cache by ID
            self.cache.set(self._id_key(user_data['user_id']), user_data)
        
        return user_data
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by ID (cached)
        
        Args:
            user_id: User ID
        
        Returns:
            User data or None
        """
        cache_key = self._id_key(user_id)
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - get from underlying store
        user_data = self.user_store.get_user_by_id(user_id)
        
        # Cache the result if found
        if user_data:
            self.cache.set(cache_key, user_data)
            # Also cache by email
            self.cache.set(self._email_key(user_data['email']), user_data)
        
        return user_data
    
    def get_all_users(self) -> list:
        """
        Get all users (not cached)
        
        Returns:
            List of user data
        """
        return self.user_store.get_all_users()
    
    def delete_user(self, email: str) -> bool:
        """
        Delete user and invalidate cache
        
        Args:
            email: Email address
        
        Returns:
            True if deleted
        """
        # Get user first to get ID
        user_data = self.user_store.get_user_by_email(email)
        
        # Delete from underlying store
        success = self.user_store.delete_user(email)
        
        if success and user_data:
            # Invalidate cache
            self._invalidate_user_cache(email, user_data['user_id'])
        
        return success
    
    def _invalidate_user_cache(self, email: str, user_id: str):
        """
        Optimized cache invalidation for a user
        Batch deletes all related cache entries efficiently
        
        Args:
            email: User email
            user_id: User ID
        """
        # Batch invalidation for better performance
        keys_to_invalidate = [
            self._email_key(email),
            self._id_key(user_id),
            self._duplicate_key(email)
        ]
        
        # Single lock acquisition for all deletes
        with self.cache.lock:
            for key in keys_to_invalidate:
                self.cache.cache.pop(key, None)  # Direct dict access, no error if missing
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all cache entries matching a pattern
        Useful for bulk invalidation operations
        
        Args:
            pattern: Pattern to match (e.g., 'email:*', 'id:*')
        """
        with self.cache.lock:
            # Find matching keys
            keys_to_delete = [
                key for key in self.cache.cache.keys()
                if self._matches_pattern(key, pattern)
            ]
            
            # Delete all matching keys
            for key in keys_to_delete:
                del self.cache.cache[key]
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """
        Check if key matches pattern (simple wildcard support)
        
        Args:
            key: Cache key
            pattern: Pattern with optional * wildcard
        
        Returns:
            True if matches
        """
        if '*' not in pattern:
            return key == pattern
        
        # Simple prefix/suffix matching
        if pattern.endswith('*'):
            return key.startswith(pattern[:-1])
        elif pattern.startswith('*'):
            return key.endswith(pattern[1:])
        else:
            # Pattern has * in middle
            parts = pattern.split('*', 1)
            return key.startswith(parts[0]) and key.endswith(parts[1])
    
    def warm_cache(self, emails: list = None, user_ids: list = None):
        """
        Warm up cache with frequently accessed users
        Pre-loads users into cache to improve initial performance
        
        Args:
            emails: List of email addresses to pre-cache
            user_ids: List of user IDs to pre-cache
        """
        if emails:
            for email in emails:
                user_data = self.user_store.get_user_by_email(email)
                if user_data:
                    self.cache.set(self._email_key(email), user_data)
                    self.cache.set(self._id_key(user_data['user_id']), user_data)
        
        if user_ids:
            for user_id in user_ids:
                user_data = self.user_store.get_user_by_id(user_id)
                if user_data:
                    self.cache.set(self._id_key(user_id), user_data)
                    self.cache.set(self._email_key(user_data['email']), user_data)
    
    def clear_all(self):
        """Clear all users and cache"""
        self.user_store.clear_all()
        self.cache.clear()
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return self.user_store.get_user_count()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries removed
        """
        return self.cache.cleanup_expired()
