# backend/api/routes/graph.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from engines.graph_engine import GraphEngine
from engines.memory_engine import MemoryEngine
from utils.learning_path import LearningPathGenerator
from app_logger.logger import get_logger

router = APIRouter()
logger = get_logger("graph-routes")

class GraphVisualizationRequest(BaseModel):
    topic: str
    depth: int = 3

graph_engine = GraphEngine()
memory_engine = MemoryEngine()
learning_path_generator = LearningPathGenerator()

@router.get("/visualize")
async def get_graph_visualization(topic: str, depth: int = 3):
    """Get graph data for visualization"""
    try:
        # Check cache
        cached = memory_engine.get_graph_data(topic)
        if cached:
            return {"data": cached, "cached": True}

        # Generate visualization data
        data = graph_engine.get_visualization_data(topic, depth)

        # Cache the data
        memory_engine.set_graph_data(topic, data)

        return {"data": data, "cached": False}

    except Exception as e:
        logger.error(f"Error getting graph visualization: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting graph visualization: {str(e)}")

@router.get("/learning-path/{topic}")
async def get_learning_path(topic: str):
    """Get learning path for a topic"""
    try:
        path = learning_path_generator.generate_learning_path(topic)
        return {"learning_path": path}

    except Exception as e:
        logger.error(f"Error getting learning path: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting learning path: {str(e)}")

@router.get("/prerequisites/{topic}")
async def get_prerequisites(topic: str):
    """Get prerequisite topics"""
    try:
        prerequisites = learning_path_generator.get_prerequisites(topic)
        return {"prerequisites": prerequisites}

    except Exception as e:
        logger.error(f"Error getting prerequisites: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting prerequisites: {str(e)}")

@router.get("/advanced-topics/{topic}")
async def get_advanced_topics(topic: str):
    """Get advanced topics that build on the given topic"""
    try:
        advanced_topics = learning_path_generator.get_advanced_topics(topic)
        return {"advanced_topics": advanced_topics}

    except Exception as e:
        logger.error(f"Error getting advanced topics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting advanced topics: {str(e)}")

@router.get("/search")
async def search_topics(q: str, limit: int = 10):
    """Search for topics in the knowledge graph"""
    try:
        # For now, return topics containing the query
        all_topics = graph_engine.graph.get_all_topics()
        matching_topics = [topic for topic in all_topics if q.lower() in topic.lower()][:limit]
        return {"topics": matching_topics, "total": len(matching_topics)}

    except Exception as e:
        logger.error(f"Error searching topics: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching topics: {str(e)}")