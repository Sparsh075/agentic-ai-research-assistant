# backend/utils/learning_path.py
from typing import List, Dict
from engines.graph_engine import GraphEngine
from engines.recommendation_engine import RecommendationEngine
from app_logger.logger import get_logger

class LearningPathGenerator:
    def __init__(self):
        self.graph_engine = GraphEngine()
        self.recommendation_engine = RecommendationEngine()
        self.logger = get_logger("learning-path")

    def generate_learning_path(self, start_topic: str, target_level: str = "advanced") -> Dict[str, List[str]]:
        """Generate learning path from beginner to advanced"""
        # Use BFS to find related topics
        related_topics = self.graph_engine.graph.bfs_traversal(start_topic, max_depth=5)

        # Categorize by difficulty
        beginner = []
        intermediate = []
        advanced = []

        for topic, depth in related_topics:
            if depth <= 1:
                beginner.append(topic)
            elif depth <= 3:
                intermediate.append(topic)
            else:
                advanced.append(topic)

        return {
            "beginner": beginner[:5],
            "intermediate": intermediate[:5],
            "advanced": advanced[:5],
            "full_path": (beginner + intermediate + advanced)[:10]
        }

    def get_prerequisites(self, topic: str) -> List[str]:
        """Get prerequisite topics for a given topic"""
        related = self.graph_engine.graph.get_related_topics(topic, limit=5)
        return [t for t, _, _ in related if t != topic][:3]

    def get_advanced_topics(self, topic: str) -> List[str]:
        """Get advanced topics that build on the given topic"""
        bfs_results = self.graph_engine.graph.bfs_traversal(topic, max_depth=4)
        return [t for t, d in bfs_results if d >= 2][:5]