# backend/api/routes/memory.py
from fastapi import APIRouter, HTTPException
from engines.memory_engine import MemoryEngine
from app_logger.logger import get_logger

router = APIRouter()
logger = get_logger("memory-routes")

memory_engine = MemoryEngine()

@router.get("/stats")
async def get_memory_stats():
    """Get memory/cache statistics"""
    try:
        stats = memory_engine.get_cache_stats()
        return {"stats": stats}

    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory stats: {str(e)}")

@router.post("/clear")
async def clear_memory():
    """Clear all caches"""
    try:
        memory_engine.clear_all_cache()
        return {"message": "All caches cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")