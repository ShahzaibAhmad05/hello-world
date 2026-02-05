"""
Example: Using the Caching Layer with User Registration System
Demonstrates cache hits, performance improvements, and cache statistics
"""

import time
from user_registration import UserRegistrationSystem
from user_storage import InMemoryUserStore
from cache_layer import CachedUserStore


def example_basic_caching():
    """Basic caching example"""
    print("\n=== Basic Caching Example ===")
    
    # Create stores
    underlying_store = InMemoryUserStore()
    cached_store = CachedUserStore(underlying_store, cache_size=100, ttl=300)
    system = UserRegistrationSystem(cached_store)
    
    # Register user
    success, msg, token = system.register_user(
        "user@example.com",
        "SecurePass123!",
        username="cacheduser"
    )
    
    print(f"Registration: {msg}")
    
    # First lookup - should hit cache (from registration)
    user1 = cached_store.get_user_by_email("user@example.com")
    print(f"First lookup: {user1['username']}")
    
    # Second lookup - cache hit
    user2 = cached_store.get_user_by_email("user@example.com")
    print(f"Second lookup: {user2['username']}")
    
    # Check stats
    stats = cached_store.get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Size: {stats['size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']}%")


def example_cache_performance():
    """Demonstrate cache performance improvement"""
    print("\n=== Cache Performance Example ===")
    
    underlying_store = InMemoryUserStore()
    
    # Add test users to underlying store
    for i in range(100):
        user = {
            'user_id': f'user{i}',
            'email': f'user{i}@example.com',
            'username': f'user{i}',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        underlying_store.save_user(user)
    
    # Test without cache
    start = time.time()
    for i in range(100):
        underlying_store.get_user_by_email(f'user{i}@example.com')
    uncached_time = time.time() - start
    
    # Test with cache
    cached_store = CachedUserStore(underlying_store, cache_size=200, ttl=300)
    
    # Warm up cache
    start = time.time()
    for i in range(100):
        cached_store.get_user_by_email(f'user{i}@example.com')
    
    # Now all cached - measure performance
    start = time.time()
    for i in range(100):
        cached_store.get_user_by_email(f'user{i}@example.com')
    cached_time = time.time() - start
    
    print(f"Uncached time: {uncached_time*1000:.2f}ms")
    print(f"Cached time: {cached_time*1000:.2f}ms")
    print(f"Speedup: {uncached_time/cached_time:.1f}x faster")
    
    stats = cached_store.get_cache_stats()
    print(f"Cache hit rate: {stats['hit_rate']}%")


def example_cache_invalidation():
    """Demonstrate cache invalidation"""
    print("\n=== Cache Invalidation Example ===")
    
    underlying_store = InMemoryUserStore()
    cached_store = CachedUserStore(underlying_store, cache_size=50, ttl=300)
    
    # Save user
    user = {
        'user_id': 'test123',
        'email': 'test@example.com',
        'username': 'testuser',
        'password_hash': 'hash',
        'salt': 'salt'
    }
    cached_store.save_user(user)
    
    print("User saved and cached")
    
    # Reset stats
    cached_store.cache.hits = 0
    cached_store.cache.misses = 0
    
    # Get user - should hit cache
    cached_store.get_user_by_email("test@example.com")
    print(f"After get: Hits={cached_store.cache.hits}, Misses={cached_store.cache.misses}")
    
    # Delete user - invalidates cache
    cached_store.delete_user("test@example.com")
    print("User deleted - cache invalidated")
    
    # Reset stats
    cached_store.cache.hits = 0
    cached_store.cache.misses = 0
    
    # Try to get user - should miss
    result = cached_store.get_user_by_email("test@example.com")
    print(f"After delete: Hits={cached_store.cache.hits}, Misses={cached_store.cache.misses}")
    print(f"User found: {result is not None}")


def example_lru_eviction():
    """Demonstrate LRU eviction"""
    print("\n=== LRU Eviction Example ===")
    
    underlying_store = InMemoryUserStore()
    cached_store = CachedUserStore(underlying_store, cache_size=3, ttl=300)
    
    # Add 3 users to fill cache
    for i in range(3):
        user = {
            'user_id': f'user{i}',
            'email': f'user{i}@example.com',
            'username': f'user{i}',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        cached_store.save_user(user)
    
    print("Cache filled with 3 users")
    print(f"Cache size: {cached_store.cache.get_stats()['size']}")
    
    # Access user0 to make it recently used
    cached_store.get_user_by_email("user0@example.com")
    print("Accessed user0 (now most recently used)")
    
    # Add user3 - should evict user1 (least recently used)
    user3 = {
        'user_id': 'user3',
        'email': 'user3@example.com',
        'username': 'user3',
        'password_hash': 'hash',
        'salt': 'salt'
    }
    cached_store.save_user(user3)
    
    print("Added user3 - triggers eviction")
    
    stats = cached_store.get_cache_stats()
    print(f"Evictions: {stats['evictions']}")
    print(f"Cache size: {stats['size']}")


def example_pattern_invalidation():
    """Demonstrate pattern-based cache invalidation"""
    print("\n=== Pattern Invalidation Example ===")
    
    underlying_store = InMemoryUserStore()
    cached_store = CachedUserStore(underlying_store, cache_size=50, ttl=300)
    
    # Add multiple users
    for i in range(5):
        user = {
            'user_id': f'user{i}',
            'email': f'user{i}@example.com',
            'username': f'user{i}',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        cached_store.save_user(user)
    
    print(f"Added 5 users - Cache size: {cached_store.cache.get_stats()['size']}")
    
    # Invalidate all email-based entries
    cached_store.invalidate_pattern("email:*")
    print("Invalidated all 'email:*' entries")
    
    print(f"Cache size after invalidation: {cached_store.cache.get_stats()['size']}")


def example_cache_warming():
    """Demonstrate cache warming"""
    print("\n=== Cache Warming Example ===")
    
    underlying_store = InMemoryUserStore()
    
    # Add users to underlying store
    for i in range(10):
        user = {
            'user_id': f'user{i}',
            'email': f'user{i}@example.com',
            'username': f'user{i}',
            'password_hash': 'hash',
            'salt': 'salt'
        }
        underlying_store.save_user(user)
    
    cached_store = CachedUserStore(underlying_store, cache_size=50, ttl=300)
    
    print("Users in underlying store (cache empty)")
    print(f"Cache size: {cached_store.cache.get_stats()['size']}")
    
    # Warm cache with frequently accessed users
    cached_store.warm_cache(
        emails=['user0@example.com', 'user1@example.com', 'user2@example.com']
    )
    
    print("\nCache warmed with 3 users")
    print(f"Cache size: {cached_store.cache.get_stats()['size']}")
    
    # Reset stats
    cached_store.cache.hits = 0
    cached_store.cache.misses = 0
    
    # Access warmed users - should all hit
    cached_store.get_user_by_email('user0@example.com')
    cached_store.get_user_by_email('user1@example.com')
    cached_store.get_user_by_email('user2@example.com')
    
    stats = cached_store.cache.get_stats()
    print(f"\nAfter accessing warmed users:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']}%")


def example_ttl_expiration():
    """Demonstrate TTL-based expiration"""
    print("\n=== TTL Expiration Example ===")
    
    underlying_store = InMemoryUserStore()
    cached_store = CachedUserStore(underlying_store, cache_size=50, ttl=2)  # 2 second TTL
    
    user = {
        'user_id': 'test123',
        'email': 'test@example.com',
        'username': 'testuser',
        'password_hash': 'hash',
        'salt': 'salt'
    }
    cached_store.save_user(user)
    
    # Reset stats
    cached_store.cache.hits = 0
    cached_store.cache.misses = 0
    
    # Immediate access - should hit cache
    cached_store.get_user_by_email("test@example.com")
    print(f"Immediate access - Hits: {cached_store.cache.hits}")
    
    # Wait for expiration
    print("Waiting 2.5 seconds for cache to expire...")
    time.sleep(2.5)
    
    # Access after expiration - should miss
    cached_store.get_user_by_email("test@example.com")
    print(f"After expiration - Misses: {cached_store.cache.misses}")
    
    # Cleanup expired entries
    removed = cached_store.cleanup_expired_cache()
    print(f"Cleaned up {removed} expired entries")


def main():
    """Run all caching examples"""
    print("=" * 60)
    print("Caching Layer - Usage Examples")
    print("=" * 60)
    
    example_basic_caching()
    example_cache_performance()
    example_cache_invalidation()
    example_lru_eviction()
    example_pattern_invalidation()
    example_cache_warming()
    example_ttl_expiration()
    
    print("\n" + "=" * 60)
    print("All caching examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
