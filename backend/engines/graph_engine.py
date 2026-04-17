# backend/engines/graph_engine.py
from typing import List, Dict, Any, Optional
from ..dsa.graph import KnowledgeGraph
from ..dsa.priority_queue import RecommendationPriorityQueue
from ..app_logger.logger import get_logger

class GraphEngine:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.recommendation_queue = RecommendationPriorityQueue()
        self.logger = get_logger("graph-engine")

    def add_topics_and_relationships(self, topics: List[str], user_query: str):
        """Add topics and relationships to graph"""
        # Add topics to graph
        for topic in topics:
            self.graph.add_topic(topic)

        # Create relationships based on query context
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                self.graph.add_relationship(topic1, topic2, weight=0.8)

        self.logger.info(f"Added {len(topics)} topics to knowledge graph")

    def get_recommendations(self, query: str, current_topic: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get ranked recommendations"""
        keywords = self._extract_keywords(query)
        if not keywords and current_topic:
            keywords = [current_topic.lower()]

        related_topics = set()
        for keyword in keywords:
            if keyword in self.graph.graph:
                bfs_results = self.graph.bfs_traversal(keyword, max_depth=2)
                related_topics.update([topic for topic, _ in bfs_results if topic != keyword])
            else:
                for topic in self.graph.get_all_topics():
                    if keyword in topic.lower() or topic.lower() in keyword:
                        bfs_results = self.graph.bfs_traversal(topic, max_depth=2)
                        related_topics.update([t for t, _ in bfs_results if t != topic])

        if current_topic and current_topic in self.graph.graph:
            related_topics.update([topic for topic, _ in self.graph.bfs_traversal(current_topic, max_depth=2) if topic != current_topic])

        if not related_topics:
            related_topics.update(self.graph.get_all_topics()[: max_results * 2])

        self.recommendation_queue.clear()
        for topic in related_topics:
            score = self._calculate_topic_score(topic, query or current_topic or topic)
            self.recommendation_queue.add_recommendation(topic, score + 0.1)

        return self.recommendation_queue.get_top_recommendations(max_results)

    def get_visualization_data(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        """Get data for graph visualization"""
        nodes = []
        edges = []
        visited = set()

        # BFS to get nodes and edges
        queue = [(topic, 0)]
        visited.add(topic)
        node_id = 0
        node_map = {}

        while queue:
            current_topic, current_depth = queue.pop(0)
            if current_depth > depth:
                break

            if current_topic not in node_map:
                node_map[current_topic] = node_id
                nodes.append({
                    'id': node_id,
                    'name': current_topic,
                    'size': len(self.graph.graph.get(current_topic, [])),
                    'color': self._get_node_color(current_depth)
                })
                node_id += 1

            # Add edges
            for neighbor, weight, rel_type in self.graph.graph.get(current_topic, []):
                if neighbor not in node_map:
                    node_map[neighbor] = node_id
                    nodes.append({
                        'id': node_id,
                        'name': neighbor,
                        'size': len(self.graph.graph.get(neighbor, [])),
                        'color': self._get_node_color(current_depth + 1)
                    })
                    node_id += 1

                edges.append({
                    'source': node_map[current_topic],
                    'target': node_map[neighbor],
                    'weight': weight,
                    'type': rel_type
                })

                if neighbor not in visited and current_depth < depth:
                    visited.add(neighbor)
                    queue.append((neighbor, current_depth + 1))

        return {'nodes': nodes, 'edges': edges}

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Simple keyword extraction - can be enhanced with NLP
        words = query.lower().split()
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'what', 'how', 'why', 'when', 'where', 'who'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords

    def _calculate_topic_score(self, topic: str, query: str) -> float:
        """Calculate relevance score for topic"""
        query_words = set(self._extract_keywords(query))
        topic_words = set(topic.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words.intersection(topic_words))
        return overlap / len(query_words)

    def _get_node_color(self, depth: int) -> str:
        """Get color for node based on depth"""
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd']
        return colors[depth % len(colors)] if depth < len(colors) else '#cccccc'