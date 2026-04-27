# backend/api/routes/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from engines.ai_engine import AIEngine
from engines.graph_engine import GraphEngine
from engines.recommendation_engine import RecommendationEngine
from engines.memory_engine import MemoryEngine
from utils.topic_extractor import TopicExtractor
from app_logger.logger import get_logger

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
    """
    Process user query with full pipeline:
    Query → AI Response → Topic Extraction → Graph Update → Recommendations → Response
    """
    # Validate input
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    query = request.query.strip()
    
    try:
        # 1. Check cache first (if enabled)
        if request.use_cache:
            cached_response = memory_engine.get_cached_query(query)
            if cached_response:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return QueryResponse(**cached_response, cached=True)

        # 2. Generate AI response
        ai_response = ai_engine.process_query(query, model=request.model)
        if not ai_response:
            raise ValueError("AI engine returned empty response")

        # 3. Extract topics from response
        topics = topic_extractor.extract_topics(query, ai_response)
        
        # Validate topic extraction
        if not topics or len(topics) < 3:
            logger.warning(f"Insufficient topics extracted: {topics}. Using fallback.")
            topics = topic_extractor._fallback_extraction(query)
        
        # Ensure 3-5 topics
        topics = topics[:5]
        if len(topics) < 3:
            logger.warning(f"Still insufficient topics after fallback: {len(topics)}")
            topics.extend([query.split()[i % len(query.split())] for i in range(3 - len(topics))])

        current_topic = topics[0] if topics else query.split()[0]

        # 4. Update knowledge graph with topics and relationships
        try:
            graph_engine.add_topics_and_relationships(topics, query)
            logger.debug(f"Updated graph with {len(topics)} topics")
        except Exception as e:
            logger.warning(f"Error updating graph: {e}")
            # Continue anyway - recommendations may still work

        # 5. Generate recommendations (graph + AI)
        recommendations = []
        try:
            recommendations = recommendation_engine.get_recommendations(query, current_topic, max_results=5)
            logger.debug(f"Generated {len(recommendations)} recommendations")
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")
            recommendations = []

        # 6. Generate explanation
        explanation = ""
        try:
            explanation = recommendation_engine.generate_explanation(recommendations, current_topic)
        except Exception as e:
            logger.warning(f"Error generating explanation: {e}")
            explanation = f"Based on '{current_topic}', we recommend exploring these related topics."

        # Prepare response
        response_data = {
            "response": ai_response,
            "topics": topics,
            "recommendations": recommendations,
            "explanation": explanation,
            "cached": False
        }

        # Cache the response (if enabled)
        if request.use_cache:
            try:
                memory_engine.set_cached_query(query, response_data)
            except Exception as e:
                logger.warning(f"Error caching response: {e}")

        logger.info(f"Processed query successfully: {query[:50]}...")
        return QueryResponse(**response_data)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing query")

@router.get("/recommendations/{topic}")
async def get_topic_recommendations(topic: str, limit: int = 5):
    """Get recommendations for a specific topic"""
    topic = topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    limit = max(3, min(5, limit))
    
    try:
        # Check cache
        cached = memory_engine.get_cached_recommendations(topic)
        if cached:
            logger.info(f"Cache hit for recommendations: {topic}")
            return {"recommendations": cached, "cached": True}

        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations("", topic, limit)

        # Cache recommendations
        try:
            memory_engine.set_cached_recommendations(topic, recommendations)
        except Exception as e:
            logger.warning(f"Error caching recommendations: {e}")

        logger.info(f"Generated {len(recommendations)} recommendations for topic: {topic}")
        return {"recommendations": recommendations, "cached": False}

    except Exception as e:
        logger.error(f"Error getting recommendations for {topic}: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")