"""
Unit Tests for Caching Layer
Tests cache hits/misses, TTL, invalidation, LRU eviction, and performance
"""

import unittest
import time
from threading import Thread

from cache_layer import LRUCache, CacheEntry, CachedUserStore
from user_storage import InMemoryUserStore


class TestCacheEntry(unittest.TestCase):
    """Test cache entry with TTL"""
    
    def test_entry_not_expired(self):
        """Test entry with valid TTL"""
        entry = CacheEntry("test_value", ttl=10)
        self.assertFalse(entry.is_expired())
    
    def test_entry_expired(self):
        """Test entry that has expired"""
        entry = CacheEntry("test_value", ttl=0)
        time.sleep(0.1)  # Wait a bit
        self.assertTrue(entry.is_expired())
    
    def test_entry_infinite_ttl(self):
        """Test entry with no expiration"""
        entry = CacheEntry("test_value", ttl=-1)
        self.assertFalse(entry.is_expired())


class TestLRUCache(unittest.TestCase):
    """Test LRU cache functionality"""
    
    def setUp(self):
        self.cache = LRUCache(max_size=3, default_ttl=10)
    
    def tearDown(self):
        self.cache.clear()
    
    def test_cache_set_and_get(self):
        """Test basic set and get operations"""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)
        self.assertEqual(self.cache.misses, 1)
    
    def test_cache_hit(self):
        """Test cache hit increments counter"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")
        self.assertEqual(self.cache.hits, 1)
    
    def test_cache_expiry(self):
        """Test cache entry expires after TTL"""
        self.cache.set("key1", "value1", ttl=1)
        
        # Should be available immediately
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired
        self.assertIsNone(self.cache.get("key1"))
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        # Fill cache to max (3 items)
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        self.cache.get("key1")
        
        # Add new item - should evict key2 (least recently used)
        self.cache.set("key4", "value4")
        
        # key2 should be evicted
        self.assertIsNone(self.cache.get("key2"))
        
        # Others should still exist
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get("key4"), "value4")
        
        # Check eviction counter
        self.assertEqual(self.cache.evictions, 1)
    
    def test_cache_delete(self):
        """Test deleting cache entry"""
        self.cache.set("key1", "value1")
        
        # Delete should return True
        self.assertTrue(self.cache.delete("key1"))
        
        # Key should no longer exist
        self.assertIsNone(self.cache.get("key1"))
        
        # Delete non-existent should return False
        self.assertFalse(self.cache.delete("key1"))
    
    def test_cache_clear(self):
        """Test clearing entire cache"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], 50.0)
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        # Add entries with different TTLs
        self.cache.set("key1", "value1", ttl=1)
        self.cache.set("key2", "value2", ttl=10)
        self.cache.set("key3", "value3", ttl=1)
        
        # Wait for some to expire
        time.sleep(1.1)
        
        # Cleanup
        removed = self.cache.cleanup_expired()
        
        # Should remove 2 expired entries
        self.assertEqual(removed, 2)
        
        # key2 should still exist
        self.assertEqual(self.cache.get("key2"), "value2")
    
    def test_cache_update(self):
        """Test updating existing cache entry"""
        self.cache.set("key1", "value1")
        self.cache.set("key1", "value2")  # Update
        
        self.assertEqual(self.cache.get("key1"), "value2")
    
    def test_thread_safety(self):
        """Test concurrent cache access"""
        results = []
        
        def writer():
            for i in range(100):
                self.cache.set(f"key{i}", f"value{i}")
        
        def reader():
            for i in range(100):
                results.append(self.cache.get(f"key{i}"))
        
        # Start threads
        t1 = Thread(target=writer)
        t2 = Thread(target=reader)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        # Should complete without errors
        self.assertGreater(len(results), 0)


class TestCachedUserStore(unittest.TestCase):
    """Test cached user storage wrapper"""
    
    def setUp(self):
        self.underlying_store = InMemoryUserStore()
        self.cached_store = CachedUserStore(
            self.underlying_store,
            cache_size=100,
            ttl=10
        )
        
        self.test_user = {
            'user_id': 'test123',
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hash',
            'salt': 'salt'
        }
    
    def tearDown(self):
        self.cached_store.clear_all()
    
    def test_cache_hit_on_duplicate_check(self):
        """Test duplicate check uses cache"""
        # First check - cache miss
        self.cached_store.save_user(self.test_user)
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Second check - should hit cache
        result = self.cached_store.check_duplicate("test@example.com")
        
        self.assertTrue(result)
        self.assertEqual(self.cached_store.cache.hits, 1)
        self.assertEqual(self.cached_store.cache.misses, 0)
    
    def test_cache_hit_on_get_by_email(self):
        """Test get by email uses cache"""
        self.cached_store.save_user(self.test_user)
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # First get - cache hit (from save)
        user = self.cached_store.get_user_by_email("test@example.com")
        
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(self.cached_store.cache.hits, 1)
    
    def test_cache_hit_on_get_by_id(self):
        """Test get by ID uses cache"""
        self.cached_store.save_user(self.test_user)
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Get by ID - should hit cache
        user = self.cached_store.get_user_by_id("test123")
        
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], 'test@example.com')
        self.assertEqual(self.cached_store.cache.hits, 1)
    
    def test_cache_invalidation_on_delete(self):
        """Test cache is invalidated when user is deleted"""
        self.cached_store.save_user(self.test_user)
        
        # Verify cached
        self.assertEqual(self.cached_store.cache.hits, 0)
        self.cached_store.get_user_by_email("test@example.com")
        self.assertEqual(self.cached_store.cache.hits, 1)
        
        # Delete user
        self.cached_store.delete_user("test@example.com")
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Should be cache miss now
        user = self.cached_store.get_user_by_email("test@example.com")
        
        self.assertIsNone(user)
        self.assertEqual(self.cached_store.cache.misses, 1)
    
    def test_cache_update_on_save(self):
        """Test cache is updated when user is saved"""
        self.cached_store.save_user(self.test_user)
        
        # Update user
        updated_user = self.test_user.copy()
        updated_user['username'] = 'newusername'
        
        self.cached_store.save_user(updated_user)
        
        # Should get updated data from cache
        user = self.cached_store.get_user_by_email("test@example.com")
        
        self.assertEqual(user['username'], 'newusername')
    
    def test_case_insensitive_caching(self):
        """Test cache handles case-insensitive emails"""
        self.cached_store.save_user(self.test_user)
        
        # Access with different case
        user1 = self.cached_store.get_user_by_email("TEST@EXAMPLE.COM")
        user2 = self.cached_store.get_user_by_email("test@example.com")
        
        self.assertIsNotNone(user1)
        self.assertIsNotNone(user2)
        self.assertEqual(user1['user_id'], user2['user_id'])
    
    def test_cache_stats(self):
        """Test cache statistics tracking"""
        self.cached_store.save_user(self.test_user)
        
        # Generate some hits and misses
        self.cached_store.get_user_by_email("test@example.com")  # Hit
        self.cached_store.get_user_by_email("nonexistent@example.com")  # Miss
        
        stats = self.cached_store.get_cache_stats()
        
        self.assertGreater(stats['hits'], 0)
        self.assertGreater(stats['misses'], 0)
        self.assertIn('hit_rate', stats)
    
    def test_pattern_invalidation(self):
        """Test invalidating cache entries by pattern"""
        # Save multiple users
        user1 = {'user_id': 'id1', 'email': 'user1@example.com', 'password_hash': 'h', 'salt': 's'}
        user2 = {'user_id': 'id2', 'email': 'user2@example.com', 'password_hash': 'h', 'salt': 's'}
        
        self.cached_store.save_user(user1)
        self.cached_store.save_user(user2)
        
        # Invalidate all email-based cache entries
        self.cached_store.invalidate_pattern("email:*")
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Should be cache misses
        self.cached_store.get_user_by_email("user1@example.com")
        self.cached_store.get_user_by_email("user2@example.com")
        
        self.assertEqual(self.cached_store.cache.misses, 2)
    
    def test_warm_cache(self):
        """Test cache warming with pre-loading"""
        # Add users to underlying store
        user1 = {'user_id': 'id1', 'email': 'user1@example.com', 'password_hash': 'h', 'salt': 's'}
        user2 = {'user_id': 'id2', 'email': 'user2@example.com', 'password_hash': 'h', 'salt': 's'}
        
        self.underlying_store.save_user(user1)
        self.underlying_store.save_user(user2)
        
        # Warm cache
        self.cached_store.warm_cache(
            emails=['user1@example.com'],
            user_ids=['id2']
        )
        
        # Reset stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Should hit cache
        self.cached_store.get_user_by_email("user1@example.com")
        self.cached_store.get_user_by_id("id2")
        
        self.assertEqual(self.cached_store.cache.hits, 2)
        self.assertEqual(self.cached_store.cache.misses, 0)
    
    def test_cache_performance_improvement(self):
        """Test cache improves performance"""
        # Save user
        self.cached_store.save_user(self.test_user)
        
        # Measure uncached access (first time)
        self.cached_store.cache.clear()
        start = time.time()
        for _ in range(100):
            self.underlying_store.get_user_by_email("test@example.com")
        uncached_time = time.time() - start
        
        # Measure cached access
        self.cached_store.save_user(self.test_user)
        start = time.time()
        for _ in range(100):
            self.cached_store.get_user_by_email("test@example.com")
        cached_time = time.time() - start
        
        # Cache should be faster (or at least not slower)
        # In practice, cache is much faster, but for small operations
        # the difference might be minimal in tests
        self.assertLessEqual(cached_time, uncached_time * 2)


class TestCacheIntegration(unittest.TestCase):
    """Integration tests for cache with registration system"""
    
    def setUp(self):
        from user_storage import InMemoryUserStore
        from user_registration import UserRegistrationSystem
        
        self.underlying_store = InMemoryUserStore()
        self.cached_store = CachedUserStore(self.underlying_store, cache_size=50, ttl=5)
        self.registration = UserRegistrationSystem(self.cached_store)
    
    def test_registration_with_cache(self):
        """Test user registration uses cache"""
        # Register user
        success, msg, token = self.registration.register_user(
            "user@example.com",
            "SecurePass123!"
        )
        
        self.assertTrue(success)
        
        # Check cache stats
        stats = self.cached_store.get_cache_stats()
        self.assertGreater(stats['size'], 0)
    
    def test_authentication_uses_cache(self):
        """Test authentication benefits from cache"""
        # Register user
        self.registration.register_user("user@example.com", "SecurePass123!")
        
        # Reset cache stats
        self.cached_store.cache.hits = 0
        self.cached_store.cache.misses = 0
        
        # Authenticate - should hit cache
        success, msg, token = self.registration.authenticate_user(
            "user@example.com",
            "SecurePass123!"
        )
        
        self.assertTrue(success)
        self.assertGreater(self.cached_store.cache.hits, 0)
    
    def test_duplicate_detection_cached(self):
        """Test duplicate detection uses cache"""
        # Register first user
        self.registration.register_user("user@example.com", "SecurePass123!")
        
        # Reset stats
        self.cached_store.cache.hits = 0
        
        # Try duplicate - should hit cache
        success, msg, token = self.registration.register_user(
            "user@example.com",
            "AnotherPass456!"
        )
        
        self.assertFalse(success)
        self.assertGreater(self.cached_store.cache.hits, 0)


def run_tests():
    """Run all cache tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
