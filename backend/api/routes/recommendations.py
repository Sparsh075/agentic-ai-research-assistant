# backend/api/routes/recommendations.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ...engines.recommendation_engine import RecommendationEngine
from ...engines.memory_engine import MemoryEngine
from ...app_logger.logger import get_logger

router = APIRouter()
logger = get_logger("recommendations-routes")

recommendation_engine = RecommendationEngine()
memory_engine = MemoryEngine()

@router.get("/{topic}")
async def get_recommendations(topic: str, limit: int = 5):
    """Get recommendations for a topic"""
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

@router.get("/learning-path/{topic}")
async def get_learning_path_recommendations(topic: str):
    """Get learning path recommendations"""
    try:
        path = recommendation_engine.get_learning_path(topic)
        return {"learning_path": path}

    except Exception as e:
        logger.error(f"Error getting learning path: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting learning path: {str(e)}")