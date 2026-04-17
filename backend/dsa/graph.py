# backend/dsa/graph.py
from collections import defaultdict, deque
import heapq

class KnowledgeGraph:
    def __init__(self):
        self.graph = defaultdict(list)  # Adjacency list: topic -> [(related_topic, weight)]
        self.topics = {}  # topic -> metadata

    def add_topic(self, topic, metadata=None):
        if topic not in self.topics:
            self.topics[topic] = metadata or {}

    def add_relationship(self, topic1, topic2, weight=1.0, relationship_type="related"):
        if topic1 not in self.graph:
            self.add_topic(topic1)
        if topic2 not in self.graph:
            self.add_topic(topic2)

        # Prevent duplicate edges in undirected graph, update weight if exists
        updated1 = False
        for i, (neighbor, w, rt) in enumerate(self.graph[topic1]):
            if neighbor == topic2:
                self.graph[topic1][i] = (topic2, min(5.0, w + weight), relationship_type)
                updated1 = True
                break
        if not updated1:
            self.graph[topic1].append((topic2, weight, relationship_type))

        updated2 = False
        for i, (neighbor, w, rt) in enumerate(self.graph[topic2]):
            if neighbor == topic1:
                self.graph[topic2][i] = (topic1, min(5.0, w + weight), relationship_type)
                updated2 = True
                break
        if not updated2:
            self.graph[topic2].append((topic1, weight, relationship_type))

    def bfs_traversal(self, start_topic, max_depth=3):
        """BFS for topic exploration and recommendations"""
        visited = set()
        queue = deque([(start_topic, 0)])  # (topic, depth)
        visited.add(start_topic)
        results = []

        while queue:
            current_topic, depth = queue.popleft()
            if depth > max_depth:
                break

            results.append((current_topic, depth))

            for neighbor, _, _ in self.graph[current_topic]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return results

    def dfs_traversal(self, start_topic, max_depth=3, visited=None):
        """DFS for deep topic exploration"""
        if visited is None:
            visited = set()

        visited.add(start_topic)
        results = [(start_topic, 0)]

        if len(results) >= max_depth:
            return results

        for neighbor, _, _ in self.graph[start_topic]:
            if neighbor not in visited:
                sub_results = self.dfs_traversal(neighbor, max_depth, visited)
                results.extend([(topic, depth + 1) for topic, depth in sub_results])

        return results[:max_depth]

    def get_related_topics(self, topic, limit=10):
        """Get directly related topics"""
        if topic not in self.graph:
            return []
        return [(t, w, rt) for t, w, rt in self.graph[topic][:limit]]

    def get_all_topics(self):
        """Get all topics in the graph"""
        return list(self.topics.keys())