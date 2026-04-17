# backend/dsa/priority_queue.py
import heapq

class RecommendationPriorityQueue:
    def __init__(self):
        self.heap = []  # Min-heap: (-score, entry_count, topic, metadata)
        self.entry_count = 0

    def add_recommendation(self, topic, score, metadata=None):
        """Add topic with priority score (higher score = higher priority)"""
        entry = (-score, self.entry_count, topic, metadata or {})
        heapq.heappush(self.heap, entry)
        self.entry_count += 1

    def get_top_recommendations(self, n=5):
        """Get top N recommendations"""
        recommendations = []
        temp_heap = self.heap.copy()

        for _ in range(min(n, len(temp_heap))):
            if temp_heap:
                neg_score, _, topic, metadata = heapq.heappop(temp_heap)
                recommendations.append({
                    'topic': topic,
                    'score': -neg_score,
                    'metadata': metadata
                })

        return recommendations

    def clear(self):
        self.heap = []
        self.entry_count = 0

    def is_empty(self):
        return len(self.heap) == 0