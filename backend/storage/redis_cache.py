# backend/storage/redis_cache.py
import json
from typing import Any, Optional, Dict
import redis
from ..app_logger.logger import get_logger

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            self.logger = get_logger("redis-cache")
            self.logger.info("Connected to Redis cache")
        except redis.ConnectionError:
            self.logger = get_logger("redis-cache")
            self.logger.warning("Redis not available, using in-memory fallback")
            self.client = None
            self.fallback_cache = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if self.client:
                value = self.client.get(key)
                return json.loads(value) if value else None
            else:
                return self.fallback_cache.get(key)
        except Exception as e:
            self.logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value with TTL in seconds"""
        try:
            if self.client:
                return self.client.setex(key, ttl, json.dumps(value))
            else:
                self.fallback_cache[key] = value
                return True
        except Exception as e:
            self.logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            if self.client:
                return bool(self.client.delete(key))
            else:
                return bool(self.fallback_cache.pop(key, None))
        except Exception as e:
            self.logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if self.client:
                return self.client.exists(key)
            else:
                return key in self.fallback_cache
        except Exception as e:
            self.logger.error(f"Error checking cache key {key}: {e}")
            return False

    def get_query_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Cache for query responses"""
        key = f"query:{hash(query)}"
        return self.get(key)

    def set_query_cache(self, query: str, response: Dict[str, Any], ttl: int = 3600):
        """Cache query response"""
        key = f"query:{hash(query)}"
        self.set(key, response, ttl)
        self.logger.debug(f"Cached query response for hash: {key}")

    def get_topic_recommendations(self, topic: str) -> Optional[list]:
        """Cache topic recommendations"""
        key = f"recommendations:{topic}"
        return self.get(key)

    def set_topic_recommendations(self, topic: str, recommendations: list, ttl: int = 1800):
        """Cache recommendations for 30 minutes"""
        key = f"recommendations:{topic}"
        self.set(key, recommendations, ttl)

    def get_graph_data(self, topic: str) -> Optional[Dict[str, Any]]:
        """Cache graph visualization data"""
        key = f"graph:{topic}"
        return self.get(key)

    def set_graph_data(self, topic: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache graph data"""
        key = f"graph:{topic}"
        self.set(key, data, ttl)

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.client:
                keys = self.client.keys(pattern)
                if keys:
                    return self.client.delete(*keys)
                return 0
            else:
                # For fallback, clear all keys containing pattern
                keys_to_delete = [k for k in self.fallback_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            self.logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.client:
                info = self.client.info()
                return {
                    "connected": True,
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "total_connections_received": info.get("total_connections_received", 0),
                    "connected_clients": info.get("connected_clients", 0)
                }
            else:
                return {
                    "connected": False,
                    "fallback_cache_size": len(self.fallback_cache)
                }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}