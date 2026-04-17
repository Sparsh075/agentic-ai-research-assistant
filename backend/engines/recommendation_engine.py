# backend/engines/recommendation_engine.py
from typing import List, Dict, Any, Optional
from ..dsa.priority_queue import RecommendationPriorityQueue
from .ai_engine import AIEngine
from .graph_engine import GraphEngine
from ..app_logger.logger import get_logger

class RecommendationEngine:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.graph_engine = GraphEngine()
        self.priority_queue = RecommendationPriorityQueue()
        self.logger = get_logger("recommendation-engine")

    def get_recommendations(self, query: str, current_topic: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get comprehensive recommendations combining graph and AI"""
        current_topic = (current_topic or query or "general").strip()
        graph_recs = self.graph_engine.get_recommendations(query, current_topic, max_results * 2)

        ai_recs = []
        if current_topic:
            ai_topics = self.ai_engine.generate_recommendations(current_topic)
            ai_recs = [
                {'topic': topic, 'score': 0.75, 'source': 'ai'}
                for topic in ai_topics if topic
            ]

        self.priority_queue.clear()
        unique_topics = set()

        for rec in graph_recs:
            if rec['topic'] in unique_topics:
                continue
            unique_topics.add(rec['topic'])
            rec['source'] = 'graph'
            # Get strongest connection for better explanation
            connections = self.graph_engine.graph.get_related_topics(rec['topic'], limit=3)
            if connections:
                strongest = max(connections, key=lambda x: x[1])
                rec['why'] = f"Strongly connected to {strongest[0]} ({strongest[2]})"
            else:
                rec['why'] = f"Related to {current_topic} through knowledge graph connections"
            self.priority_queue.add_recommendation(rec['topic'], rec['score'] * 1.3, rec)

        for rec in ai_recs:
            if rec['topic'] in unique_topics:
                continue
            unique_topics.add(rec['topic'])
            rec['why'] = f"AI-suggested topic related to {current_topic}"
            self.priority_queue.add_recommendation(rec['topic'], rec['score'], rec)

        recs = self.priority_queue.get_top_recommendations(max_results)

        if len(recs) < 3 and current_topic:
            additional_ai = self.ai_engine.generate_recommendations(current_topic)
            for topic in additional_ai:
                if len(recs) >= max_results:
                    break
                if topic and topic not in unique_topics:
                    unique_topics.add(topic)
                    recs.append({
                        'topic': topic,
                        'score': 0.6,
                        'source': 'ai',
                        'why': f"Additional AI suggestion related to {current_topic}"
                    })

        if not recs and current_topic:
            recs.append({
                'topic': current_topic,
                'score': 0.5,
                'source': 'fallback',
                'why': "Fallback recommendation based on your current topic"
            })

        return recs[:max_results]

    def generate_explanation(self, recommendations: List[Dict[str, Any]], current_topic: str) -> str:
        """Generate explanation for the recommendations"""
        if not recommendations:
            return "No recommendations available at this time."

        sources = set(r.get('source', 'unknown') for r in recommendations)
        explanation = f"Based on '{current_topic or 'your query'}', these topics are recommended. "

        if 'graph' in sources:
            explanation += "Some recommendations come from knowledge graph connections. "
        if 'ai' in sources:
            explanation += "Others are AI-generated for deeper learning. "

        return explanation.strip()

    def get_learning_path(self, start_topic: str) -> Dict[str, List[str]]:
        """Generate learning path from beginner to advanced"""
        # Use BFS to find related topics
        related_topics = self.graph_engine.graph.bfs_traversal(start_topic, max_depth=5)

        # Categorize by difficulty (this would be enhanced with metadata)
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