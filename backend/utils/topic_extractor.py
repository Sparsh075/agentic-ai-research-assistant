# backend/utils/topic_extractor.py
from typing import List, Dict
import re

from engines.ai_engine import AIEngine
from app_logger.logger import get_logger

class TopicExtractor:
    """Extract clean, technical topics from queries and responses"""
    
    def __init__(self):
        self.ai_engine = AIEngine()
        self.logger = get_logger("topic-extractor")

    def extract_topics(self, user_query: str, ai_response: str) -> List[str]:
        """
        Extract 3-5 clean topics from user query and AI response.
        Delegates to AIEngine for LLM-based extraction.
        """
        topics = self.ai_engine.extract_topics_from_response(user_query, ai_response)
        
        # Validate result
        if not topics:
            self.logger.warning("No topics extracted, using fallback")
            topics = self._fallback_extraction(user_query)
        
        return topics[:5]  # Ensure max 5

    def _fallback_extraction(self, text: str) -> List[str]:
        """
        Fallback extraction when LLM fails.
        Uses regex to extract potential topics from text.
        """
        if not text or not text.strip():
            return []
        
        topics = []
        seen = set()
        
        # Extract capitalized terms (potential technical terms)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Extract multi-word phrases
        phrases = re.findall(r'\b[a-z]+(?:\s+[a-z]+){1,2}\b', text, re.IGNORECASE)
        
        for term in capitalized + phrases:
            clean = term.strip().lower()
            if 2 <= len(clean) <= 30 and clean not in seen and len(clean.split()) <= 3:
                topics.append(clean)
                seen.add(clean)
                if len(topics) >= 5:
                    break
        
        # Ensure at least 3 topics
        while len(topics) < 3:
            words = text.split()
            for word in words:
                clean = word.strip().lower()
                if 4 <= len(clean) <= 30 and clean not in seen:
                    topics.append(clean)
                    seen.add(clean)
                    if len(topics) >= 3:
                        break
            break
        
        return topics[:5]