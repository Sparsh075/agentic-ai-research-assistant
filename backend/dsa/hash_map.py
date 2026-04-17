# backend/dsa/hash_map.py
class TopicCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []  # For LRU eviction

    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]

        self.cache[key] = value
        self.access_order.append(key)

    def contains(self, key):
        return key in self.cache

    def remove(self, key):
        if key in self.cache:
            self.access_order.remove(key)
            del self.cache[key]

    def clear(self):
        self.cache.clear()
        self.access_order.clear()

    def size(self):
        return len(self.cache)