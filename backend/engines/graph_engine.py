# backend/engines/graph_engine.py
from typing import List, Dict, Any, Optional
from dsa.graph import KnowledgeGraph
from dsa.priority_queue import RecommendationPriorityQueue
from app_logger.logger import get_logger

class GraphEngine:
    """
    Graph Engine for managing knowledge graph and generating recommendations
    using graph-based algorithms (BFS with weighted edges).
    """
    
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'what', 'how', 'why', 'when', 'where', 'who', 'which', 'that', 'this', 'these', 'those'
    }

    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GraphEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.graph = KnowledgeGraph()
        self.recommendation_queue = RecommendationPriorityQueue()
        self.logger = get_logger("graph-engine")
        self._initialized = True

    def add_topics_and_relationships(self, topics: List[str], user_query: str) -> None:
        """
        Add topics to graph and create relationships between them.
        All topics extracted from a single response are related.
        """
        if not topics:
            self.logger.warning("No topics to add to graph")
            return
        
        # Add each topic
        for topic in topics:
            self.graph.add_topic(topic)

        # Create relationships between all topic pairs (fully connected)
        # This models the fact that they came from the same context
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i + 1:]:
                self.graph.add_relationship(topic1, topic2, weight=1.0, relationship_type="context")

        self.logger.info(f"Added {len(topics)} topics to knowledge graph with relationships")

    def get_recommendations(self, query: str, current_topic: Optional[str] = None, 
                          max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Generate ranked recommendations using graph-based BFS traversal.
        Prioritizes topics by edge weight (stronger connections = higher priority).
        """
        if max_results < 3:
            max_results = 3
        if max_results > 5:
            max_results = 5

        # Determine starting point for recommendation search
        start_topic = (current_topic or query or "").strip().lower()
        
        if not start_topic:
            # Fallback: recommend most connected topics
            return self._recommend_popular_topics(max_results)

        # Get related topics via BFS (sorted by weight)
        recommended_topics = []
        seen = set()
        
        # Try to find in graph
        if start_topic in self.graph.graph:
            # Direct neighbors sorted by weight
            neighbors = self.graph.get_neighbors_sorted_by_weight(start_topic, descending=True)
            for neighbor, weight, _ in neighbors:
                if neighbor not in seen and neighbor != start_topic:
                    recommended_topics.append({
                        'topic': neighbor,
                        'score': weight / self.graph.max_edge_weight,  # Normalize to 0-1
                        'depth': 1,
                        'source': 'graph'
                    })
                    seen.add(neighbor)
                    if len(recommended_topics) >= max_results * 2:
                        break
            
            # Expand search to depth 2 if needed
            if len(recommended_topics) < max_results:
                bfs_results = self.graph.bfs_traversal(start_topic, max_depth=2)
                for topic, depth in bfs_results:
                    if topic not in seen and topic != start_topic and depth > 1:
                        neighbors = self.graph.get_related_topics(topic, limit=1)
                        weight = neighbors[0][1] if neighbors else 0.5
                        recommended_topics.append({
                            'topic': topic,
                            'score': (weight / self.graph.max_edge_weight) * (0.8 ** (depth - 1)),
                            'depth': depth,
                            'source': 'graph'
                        })
                        seen.add(topic)
        else:
            # Topic not in graph: find most similar topics or use popular ones
            return self._recommend_popular_topics(max_results)

        # Sort by score and take top results
        recommended_topics.sort(key=lambda x: x['score'], reverse=True)
        result_recs = recommended_topics[:max_results]

        # Ensure minimum 3 recommendations
        if len(result_recs) < 3:
            result_recs.extend(self._recommend_popular_topics(max_results - len(result_recs)))

        return result_recs[:max_results]

    def _recommend_popular_topics(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Recommend most connected (popular) topics when start topic not found"""
        # Score topics by number of connections
        topic_scores = {}
        for topic in self.graph.get_all_topics():
            neighbors = self.graph.get_related_topics(topic, limit=None)
            total_weight = sum(weight for _, weight, _ in neighbors) if neighbors else 0.0
            topic_scores[topic] = total_weight

        # Sort by score
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for topic, score in sorted_topics[:max_results]:
            result.append({
                'topic': topic,
                'score': min(1.0, score / self.graph.max_edge_weight),
                'depth': 0,
                'source': 'popular'
            })
        
        return result

    def get_visualization_data(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        """
        Generate node-link data for graph visualization (D3.js/force-graph compatible).
        
        Returns:
            {nodes: [{id, name, size, color, fx?, fy?}], links: [{source, target, weight}]}
        """
        topic = topic.strip().lower()
        if topic not in self.graph.graph and topic not in self.graph.topics:
            return {'nodes': [], 'links': []}

        nodes = []
        links = []
        visited = set()
        node_id_map = {}  # topic -> id
        node_counter = [0]  # Use list to allow mutation in nested function

        # BFS to collect nodes and edges
        queue = [(topic, 0)]
        visited.add(topic)

        while queue:
            current_topic, current_depth = queue.pop(0)
            
            if current_depth > depth:
                continue

            # Add node if not seen
            if current_topic not in node_id_map:
                node_id = node_counter[0]
                node_id_map[current_topic] = node_id
                
                neighbors = self.graph.get_related_topics(current_topic, limit=None)
                node_size = len(neighbors) if neighbors else 1
                
                nodes.append({
                    'id': node_id,
                    'name': current_topic,
                    'size': node_size,
                    'color': self._get_node_color(current_depth),
                    'depth': current_depth,
                    'neighbors': len(neighbors)
                })
                node_counter[0] += 1

            # Add edges to neighbors
            neighbors = self.graph.get_neighbors_sorted_by_weight(current_topic, descending=True)
            for neighbor, weight, rel_type in neighbors:
                if neighbor not in node_id_map and current_depth < depth:
                    node_id = node_counter[0]
                    node_id_map[neighbor] = node_id
                    
                    neighbor_neighbors = self.graph.get_related_topics(neighbor, limit=None)
                    node_size = len(neighbor_neighbors) if neighbor_neighbors else 1
                    
                    nodes.append({
                        'id': node_id,
                        'name': neighbor,
                        'size': node_size,
                        'color': self._get_node_color(current_depth + 1),
                        'depth': current_depth + 1,
                        'neighbors': len(neighbor_neighbors)
                    })
                    node_counter[0] += 1
                    
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, current_depth + 1))

                # Add link
                if neighbor in node_id_map:
                    links.append({
                        'source': node_id_map[current_topic],
                        'target': node_id_map[neighbor],
                        'weight': weight,
                        'value': weight,  # For force-graph
                        'type': rel_type
                    })

        return {'nodes': nodes, 'links': links}

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        if not query or not query.strip():
            return []
        
        words = query.lower().split()
        keywords = [
            word.strip('.,!?;:"\'-') 
            for word in words 
            if word not in self.STOP_WORDS and len(word) > 2
        ]
        return keywords

    def _calculate_topic_score(self, topic: str, query: str) -> float:
        """Calculate relevance score for topic based on query overlap"""
        query_words = set(self._extract_keywords(query))
        topic_words = set(topic.lower().split())

        if not query_words or not topic_words:
            return 0.0

        overlap = len(query_words.intersection(topic_words))
        return overlap / len(query_words) if query_words else 0.0

    def _get_node_color(self, depth: int) -> str:
        """
        Get color for node based on depth.
        Gradient from deep red (root) to light blue (periphery).
        """
        colors = [
            '#DC2626',  # Red
            '#DC143C',  # Crimson
            '#E74C3C',  # Dark Red
            '#FF6B6B',  # Light Red
            '#FFA07A',  # Light Salmon
            '#FFB6C1',  # Light Pink
        ]
        return colors[min(depth, len(colors) - 1)]