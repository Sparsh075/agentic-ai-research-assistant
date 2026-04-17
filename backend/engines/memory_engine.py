# backend/engines/memory_engine.py
from typing import Any, Optional, Dict
from ..dsa.hash_map import TopicCache
from ..app_logger.logger import get_logger

class MemoryEngine:
    def __init__(self):
        self.query_cache = TopicCache(max_size=500)  # Cache query responses
        self.topic_cache = TopicCache(max_size=1000)  # Cache topic data
        self.recommendation_cache = TopicCache(max_size=200)  # Cache recommendations
        self.logger = get_logger("memory-engine")

    def get_cached_query(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached query response"""
        return self.query_cache.get(query_hash)

    def set_cached_query(self, query_hash: str, response: Dict[str, Any]):
        """Cache query response"""
        self.query_cache.put(query_hash, response)
        self.logger.debug(f"Cached query response for hash: {query_hash}")

    def get_cached_topics(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached topic data"""
        return self.topic_cache.get(topic)

    def set_cached_topics(self, topic: str, data: Dict[str, Any]):
        """Cache topic data"""
        self.topic_cache.put(topic, data)

    def get_cached_recommendations(self, topic: str) -> Optional[list]:
        """Get cached recommendations"""
        return self.recommendation_cache.get(topic)

    def set_cached_recommendations(self, topic: str, recommendations: list):
        """Cache recommendations"""
        self.recommendation_cache.put(topic, recommendations)

    def get_graph_data(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get cached graph data"""
        return self.topic_cache.get(f"graph_{topic}")

    def set_graph_data(self, topic: str, data: Dict[str, Any], ttl: int = 3600):
        """Cache graph data"""
        self.topic_cache.put(f"graph_{topic}", data)

    def clear_all_cache(self):
        """Clear all caches"""
        self.query_cache.clear()
        self.topic_cache.clear()
        self.recommendation_cache.clear()
        self.logger.info("Cleared all caches")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "query_cache_size": self.query_cache.size(),
            "topic_cache_size": self.topic_cache.size(),
            "recommendation_cache_size": self.recommendation_cache.size()
        }