# backend/engines/recommendation_engine.py
"""Recommendation Engine combining graph-based and AI-based recommendations"""

from typing import List, Dict, Any, Optional
from dsa.priority_queue import RecommendationPriorityQueue
from engines.ai_engine import AIEngine
from engines.graph_engine import GraphEngine
from app_logger.logger import get_logger

class RecommendationEngine:
    """
    Generate recommendations using:
    1. Primary: Graph-based (topics strongly connected in knowledge graph)
    2. Secondary: AI-based (LLM suggestions for related topics)
    3. Fallback: Popular topics (most connected in graph)
    """
    
    def __init__(self):
        self.ai_engine = AIEngine()
        self.graph_engine = GraphEngine()
        self.priority_queue = RecommendationPriorityQueue()
        self.logger = get_logger("recommendation-engine")

    def get_recommendations(self, query: str, current_topic: Optional[str] = None, 
                          max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Generate ranked recommendations combining graph and AI approaches.
        
        Returns:
            List of up to max_results recommendation dicts with: topic, score, source, explanation
        """
        # Normalize max_results
        max_results = max(3, min(5, max_results))
        
        # Determine starting point
        topic = (current_topic or query or "").strip().lower()
        
        if not topic:
            self.logger.warning("No topic provided for recommendations")
            return self._get_fallback_recommendations(max_results)

        # Get graph-based recommendations (primary)
        graph_recs = self._get_graph_recommendations(topic, max_results)
        
        # Get AI-based recommendations (secondary)
        ai_recs = self._get_ai_recommendations(topic, max_results)
        
        # Merge and rank
        combined = self._merge_and_rank_recommendations(
            graph_recs, 
            ai_recs, 
            topic, 
            max_results
        )
        
        return combined[:max_results]

    def _get_graph_recommendations(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """Get recommendations from knowledge graph via BFS"""
        try:
            graph_recs = self.graph_engine.get_recommendations("", topic, limit)
            
            # Enhance with explanations
            for rec in graph_recs:
                if rec['source'] != 'popular':
                    # Find strongest connection for explanation
                    neighbors = self.graph_engine.graph.get_related_topics(topic, limit=1)
                    if neighbors:
                        _, weight, rel_type = neighbors[0]
                        rec['explanation'] = f"Strongly connected in knowledge graph (weight: {weight:.1f})"
                    else:
                        rec['explanation'] = f"Related through graph connections"
                else:
                    rec['explanation'] = "Popular topic in knowledge graph"
            
            return graph_recs
            
        except Exception as e:
            self.logger.error(f"Error getting graph recommendations: {e}")
            return []

    def _get_ai_recommendations(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """Get recommendations from AI engine"""
        try:
            ai_topics = self.ai_engine.generate_recommendations(topic, max_recommendations=limit)
            
            ai_recs = [
                {
                    'topic': t,
                    'score': 0.7,  # Default AI score
                    'source': 'ai',
                    'explanation': f"AI-suggested topic related to {topic}"
                }
                for t in ai_topics if t and t.strip()
            ]
            
            return ai_recs
            
        except Exception as e:
            self.logger.error(f"Error getting AI recommendations: {e}")
            return []

    def _merge_and_rank_recommendations(self, graph_recs: List[Dict[str, Any]], 
                                       ai_recs: List[Dict[str, Any]], 
                                       topic: str, max_results: int) -> List[Dict[str, Any]]:
        """Merge graph and AI recommendations, rank by score"""
        merged = {}  # topic -> rec dict
        
        # Add graph recommendations (higher priority)
        for rec in graph_recs:
            rec_topic = rec.get('topic', '').strip()
            if rec_topic and rec_topic not in merged:
                merged[rec_topic] = rec
        
        # Add AI recommendations (fill gaps)
        for rec in ai_recs:
            rec_topic = rec.get('topic', '').strip()
            if rec_topic and rec_topic not in merged:
                merged[rec_topic] = rec
        
        # Sort by score
        ranked = sorted(merged.values(), key=lambda r: r.get('score', 0), reverse=True)
        
        # Ensure minimum 3 and maximum 5
        result = ranked[:max_results]
        if len(result) < 3:
            result.extend(self._get_fallback_recommendations(3 - len(result)))
        
        return result[:max_results]

    def _get_fallback_recommendations(self, max_results: int = 3) -> List[Dict[str, Any]]:
        """Fallback: recommend most popular topics"""
        try:
            popular = self.graph_engine._recommend_popular_topics(max_results)
            for rec in popular:
                rec['explanation'] = "Popular topic in knowledge graph"
            return popular
        except Exception as e:
            self.logger.error(f"Error getting fallback recommendations: {e}")
            return []

    def generate_explanation(self, recommendations: List[Dict[str, Any]], 
                            current_topic: str) -> str:
        """Generate human-readable explanation for recommendations"""
        if not recommendations:
            return "No recommendations available at this time."
        
        if not current_topic:
            current_topic = "your query"
        
        sources = set(r.get('source', 'unknown') for r in recommendations)
        
        explanation = f"Based on '{current_topic}', we recommend exploring these topics. "
        
        if 'graph' in sources:
            explanation += "Our knowledge graph suggests these based on similar topics you've explored. "
        if 'ai' in sources:
            explanation += "AI analysis suggests these related areas for deeper learning. "
        
        return explanation.strip()

    def get_learning_path(self, start_topic: str) -> Dict[str, List[str]]:
        """
        Generate learning path from beginner to advanced topics.
        Uses BFS traversal to find progressive depth levels.
        """
        start_topic = start_topic.strip().lower()
        
        if start_topic not in self.graph_engine.graph.graph:
            return {
                'beginner': [],
                'intermediate': [],
                'advanced': []
            }
        
        try:
            # Use BFS to find topics at different depths
            bfs_results = self.graph_engine.graph.bfs_traversal(start_topic, max_depth=5)
            
            # Group by depth
            beginner = [topic for topic, depth in bfs_results if depth <= 1]
            intermediate = [topic for topic, depth in bfs_results if 1 < depth <= 3]
            advanced = [topic for topic, depth in bfs_results if depth > 3]
            
            return {
                'beginner': beginner[:5],
                'intermediate': intermediate[:5],
                'advanced': advanced[:5]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating learning path: {e}")
            return {
                'beginner': [],
                'intermediate': [],
                'advanced': []
            }