# backend/dsa/graph.py
"""Knowledge Graph using adjacency list with weighted, undirected edges"""

from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Set
import heapq

class KnowledgeGraph:
    """
    Knowledge Graph implementation using adjacency list.
    - Undirected graph with weighted edges
    - Weights increment on repeated relations (up to max 5.0)
    - Supports BFS/DFS traversal and nearest neighbor queries
    """
    
    def __init__(self, max_edge_weight: float = 5.0):
        # Adjacency list: topic -> [(neighbor, weight, relationship_type)]
        self.graph = defaultdict(list)
        # Topic metadata: topic -> {metadata dict}
        self.topics = {}
        self.max_edge_weight = max_edge_weight

    def add_topic(self, topic: str, metadata: Optional[Dict] = None) -> None:
        """Add a topic node to the graph"""
        topic = topic.strip().lower()
        if not topic:
            return
        if topic not in self.topics:
            self.topics[topic] = metadata or {}

    def add_relationship(self, topic1: str, topic2: str, weight: float = 1.0, 
                        relationship_type: str = "related") -> None:
        """
        Add weighted undirected edge between two topics.
        If edge exists, increment weight (capped at max_edge_weight).
        """
        topic1 = topic1.strip().lower()
        topic2 = topic2.strip().lower()
        
        if not topic1 or not topic2 or topic1 == topic2:
            return

        # Ensure both topics exist
        self.add_topic(topic1)
        self.add_topic(topic2)

        # Update or add edge from topic1 to topic2
        self._update_edge(topic1, topic2, weight, relationship_type)
        # Update or add reverse edge (undirected)
        self._update_edge(topic2, topic1, weight, relationship_type)

    def _update_edge(self, source: str, target: str, weight: float, 
                    relationship_type: str) -> None:
        """Update or add edge between source and target"""
        for i, (neighbor, w, rt) in enumerate(self.graph[source]):
            if neighbor == target:
                # Edge exists: increment weight (capped)
                new_weight = min(self.max_edge_weight, w + weight)
                self.graph[source][i] = (target, new_weight, relationship_type)
                return
        
        # Edge doesn't exist: add new edge
        self.graph[source].append((target, weight, relationship_type))

    def get_neighbors_sorted_by_weight(self, topic: str, descending: bool = True) -> List[Tuple[str, float, str]]:
        """
        Get all neighbors of a topic, sorted by edge weight.
        
        Args:
            topic: The topic to get neighbors for
            descending: If True, highest weights first
            
        Returns:
            List of (neighbor, weight, relationship_type) tuples
        """
        topic = topic.strip().lower()
        if topic not in self.graph:
            return []
        
        neighbors = self.graph[topic]
        # Sort by weight (descending by default)
        return sorted(neighbors, key=lambda x: x[1], reverse=descending)

    def bfs_traversal(self, start_topic: str, max_depth: int = 3) -> List[Tuple[str, int]]:
        """
        BFS traversal from start_topic, visiting neighbors sorted by weight.
        
        Returns:
            List of (topic, depth) tuples
        """
        start_topic = start_topic.strip().lower()
        if start_topic not in self.graph and start_topic not in self.topics:
            return []

        visited = {start_topic}
        queue = deque([(start_topic, 0)])
        results = []

        while queue:
            current_topic, depth = queue.popleft()
            results.append((current_topic, depth))

            if depth >= max_depth:
                continue

            # Get neighbors sorted by weight (strongest connections first)
            neighbors = self.get_neighbors_sorted_by_weight(current_topic, descending=True)
            
            for neighbor, weight, _ in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return results

    def dfs_traversal(self, start_topic: str, max_depth: int = 3, 
                     visited: Optional[Set[str]] = None) -> List[Tuple[str, int]]:
        """
        DFS traversal from start_topic, visiting neighbors sorted by weight.
        
        Returns:
            List of (topic, depth) tuples
        """
        start_topic = start_topic.strip().lower()
        
        if visited is None:
            visited = set()

        if start_topic in visited or start_topic not in self.graph and start_topic not in self.topics:
            return []

        visited.add(start_topic)
        results = [(start_topic, 0)]

        if len(visited) >= max_depth * 5:  # Rough limit
            return results

        # Get neighbors sorted by weight
        neighbors = self.get_neighbors_sorted_by_weight(start_topic, descending=True)
        
        for neighbor, _, _ in neighbors:
            if neighbor not in visited:
                sub_results = self.dfs_traversal(neighbor, max_depth - 1, visited)
                results.extend([(topic, depth + 1) for topic, depth in sub_results])

        return results

    def get_related_topics(self, topic: str, limit: int = 10) -> List[Tuple[str, float, str]]:
        """
        Get directly related topics (immediate neighbors), sorted by weight.
        
        Returns:
            List of (topic, weight, relationship_type) tuples
        """
        topic = topic.strip().lower()
        if topic not in self.graph:
            return []
        
        # Return neighbors sorted by weight
        neighbors = self.get_neighbors_sorted_by_weight(topic, descending=True)
        return neighbors[:limit]

    def get_all_topics(self) -> List[str]:
        """Get list of all topics in graph"""
        return list(self.topics.keys())

    def get_graph_size(self) -> Dict[str, int]:
        """Get graph statistics"""
        num_edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        return {
            "num_topics": len(self.topics),
            "num_edges": num_edges,
            "avg_degree": num_edges * 2 / max(len(self.topics), 1)
        }

    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between two topics using BFS"""
        start = start.strip().lower()
        end = end.strip().lower()
        
        if start not in self.graph or end not in self.graph:
            return None
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path
            
            for neighbor, _, _ in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None