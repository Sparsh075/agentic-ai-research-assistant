# backend/api/routes/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ...engines.ai_engine import AIEngine
from ...engines.graph_engine import GraphEngine
from ...engines.recommendation_engine import RecommendationEngine
from ...engines.memory_engine import MemoryEngine
from ...utils.topic_extractor import TopicExtractor
from ...app_logger.logger import get_logger

router = APIRouter()
logger = get_logger("query-routes")

class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    use_cache: bool = True

class QueryResponse(BaseModel):
    response: str
    topics: List[str]
    recommendations: List[Dict[str, Any]]
    explanation: str
    cached: bool = False

ai_engine = AIEngine()
graph_engine = GraphEngine()
recommendation_engine = RecommendationEngine()
memory_engine = MemoryEngine()
topic_extractor = TopicExtractor()

@router.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query with AI and graph enhancements"""
    try:
        # Check cache first
        if request.use_cache:
            cached_response = memory_engine.get_cached_query(request.query)
            if cached_response:
                logger.info("Returning cached response")
                return QueryResponse(**cached_response, cached=True)

        # Process query with AI
        response = ai_engine.process_query(request.query, model=request.model)

        # Extract topics
        topics = topic_extractor.extract_topics(request.query, response)

        # Ensure we have at least one stable topic to drive graph and recommendations
        if not topics:
            topics = topic_extractor.extract_topics_from_text(request.query)

        current_topic = topics[0] if topics else request.query.strip()

        # Update knowledge graph
        try:
            graph_engine.add_topics_and_relationships(topics, request.query)
        except Exception as e:
            logger.warning(f"Error updating graph: {e}")

        # Generate recommendations using both query and extracted topic
        try:
            recommendations = recommendation_engine.get_recommendations(request.query, current_topic)
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")
            recommendations = []

        # Generate explanation for recommendations
        try:
            explanation = recommendation_engine.generate_explanation(recommendations, current_topic)
        except Exception as e:
            logger.warning(f"Error generating explanation: {e}")
            explanation = "Recommendations generated based on your query."

        # Prepare response
        response_data = {
            "response": response,
            "topics": topics,
            "recommendations": recommendations,
            "explanation": explanation,
            "cached": False
        }

        # Cache the response
        if request.use_cache:
            memory_engine.set_cached_query(request.query, response_data)

        return QueryResponse(**response_data)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/recommendations/{topic}")
async def get_topic_recommendations(topic: str, limit: int = 5):
    """Get recommendations for a specific topic"""
    try:
        # Check cache
        cached = memory_engine.get_cached_recommendations(topic)
        if cached:
            return {"recommendations": cached, "cached": True}

        recommendations = recommendation_engine.get_recommendations("", topic, limit)

        # Cache recommendations
        memory_engine.set_cached_recommendations(topic, recommendations)

        return {"recommendations": recommendations, "cached": False}

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")