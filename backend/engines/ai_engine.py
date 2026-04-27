# backend/engines/ai_engine.py
from typing import List, Dict, Any, Optional
import json
import re
from llm.llm_router import generate_response
from app_logger.logger import get_logger

class AIEngine:
    """AI Engine for processing queries, extracting topics, and generating recommendations"""
    
    def __init__(self):
        self.logger = get_logger("ai-engine")
        self.max_retries = 2

    def process_query(self, query: str, context: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Process user query with optional knowledge graph context.
        
        Args:
            query: User question
            context: Optional knowledge graph context
            model: Optional model to use
            
        Returns:
            Generated response string
        """
        if not query or not query.strip():
            return "Please provide a valid question."
            
        if context:
            enhanced_prompt = f"""Context from knowledge graph:
{context}

User Query: {query}

Provide a comprehensive answer using the context above when relevant. Be concise and accurate."""
        else:
            enhanced_prompt = query

        try:
            response = generate_response(enhanced_prompt, model=model)
            if not response or not response.strip():
                return "Unable to generate a response. Please try again."
            self.logger.info(f"Generated response for query: {query[:50]}...")
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your query. Please try again."

    def _parse_json_array(self, response: str) -> List[str]:
        """
        Safely parse JSON array from LLM response.
        Handles malformed JSON with multiple retry strategies.
        """
        if not response or not response.strip():
            return []
            
        text = response.strip()
        
        # Try to extract JSON array
        match = re.search(r'\[.*\]', text, flags=re.S)
        if match:
            text = match.group(0)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
            return []
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON array from LLM response: {text[:100]}")
            # Fallback: try to extract quoted strings
            quoted = re.findall(r'"([^"]+)"', text)
            return quoted if quoted else []

    def extract_topics_from_response(self, user_query: str, ai_response: str) -> List[str]:
        """
        Extract 3-5 clean, technical topics from query and response using LLM.
        CRITICAL: Returns exactly 3-5 topics, max 3 words each, no duplicates.
        """
        if not ai_response or not ai_response.strip():
            return self._extract_fallback_topics(user_query)
            
        prompt = f"""Extract 3-5 key technical topics/concepts from this query and response.

Requirements:
- Return EXACTLY 3-5 topics
- Each topic: 1-3 words max, lowercase
- Only technical/domain terms
- No duplicates
- No common words (the, is, a, etc)
- Format: ["topic1", "topic2", "topic3", "topic4", "topic5"]

Query: {user_query[:200]}
Response: {ai_response[:300]}

Topics (JSON array only):"""

        for attempt in range(self.max_retries):
            try:
                raw_response = generate_response(
                    prompt, 
                    model="llama3:8b", 
                    options={"max_tokens": 100}
                )
                topics = self._parse_json_array(raw_response)
                
                if not topics:
                    continue
                    
                cleaned = self._normalize_topics(topics)
                if len(cleaned) >= 3:
                    return cleaned[:5]
                    
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                continue

        # Fallback to regex-based extraction
        return self._extract_fallback_topics(user_query + " " + ai_response)

    def _normalize_topics(self, topics: List[str]) -> List[str]:
        """Normalize and deduplicate topics"""
        cleaned = []
        seen = set()
        
        stop_words = {'the', 'is', 'are', 'was', 'were', 'be', 'been', 'a', 'an', 'and', 'or', 'of', 'for', 'to', 'in', 'on', 'at', 'by', 'with'}
        
        for topic in topics:
            if not isinstance(topic, str):
                continue
                
            # Clean: lowercase, remove special chars, strip whitespace
            t = topic.strip().lower()
            t = re.sub(r'[^a-z0-9\s]', '', t)
            t = re.sub(r'\s{2,}', ' ', t).strip()
            
            # Remove stop words from edges
            words = t.split()
            while words and words[0] in stop_words:
                words.pop(0)
            while words and words[-1] in stop_words:
                words.pop()
            
            t = ' '.join(words)
            
            # Enforce length constraints
            if not t or len(t) < 2 or len(t) > 30:
                continue
            if len(t.split()) > 3:
                t = ' '.join(t.split()[:3])
            if t in seen:
                continue
                
            seen.add(t)
            cleaned.append(t)
            
        return cleaned[:5]

    def _extract_fallback_topics(self, text: str) -> List[str]:
        """Fallback: Extract topics using regex when LLM fails"""
        if not text or not text.strip():
            return []
            
        # Extract capitalized phrases (likely named entities/concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Extract multi-word technical terms
        technical_terms = re.findall(r'\b[a-z]+(?:_[a-z]+|\s+[a-z]+)*\b', text, re.IGNORECASE)
        
        candidates = list(set(capitalized + technical_terms))
        topics = []
        
        for candidate in candidates[:20]:  # Process top 20 candidates
            clean = candidate.strip().lower()
            if 3 <= len(clean) <= 30 and len(clean.split()) <= 3:
                topics.append(clean)
                if len(topics) >= 5:
                    break
        
        # Ensure minimum 3 topics
        while len(topics) < 3 and len(candidates) > len(topics):
            for candidate in candidates[len(topics):]:
                clean = candidate.strip().lower()
                if clean not in topics and 2 <= len(clean) <= 30:
                    topics.append(clean)
                    if len(topics) >= 3:
                        break
        
        return topics[:5]

    def generate_recommendations(self, current_topic: str, max_recommendations: int = 5) -> List[str]:
        """Generate 3-5 related topic recommendations using LLM"""
        if not current_topic or not current_topic.strip():
            return []
            
        prompt = f"""Given the topic "{current_topic}", suggest {max_recommendations} related topics for learning.
Consider:
- Prerequisites
- Advanced concepts
- Related technologies
- Complementary skills

Return EXACTLY {max_recommendations} topics as JSON array, each 1-3 words:
["topic1", "topic2", "topic3", "topic4", "topic5"]

Topics only (JSON array):"""

        try:
            raw_response = generate_response(
                prompt, 
                model="llama3:8b", 
                options={"max_tokens": 100}
            )
            recommendations = self._parse_json_array(raw_response)
            if recommendations:
                cleaned = self._normalize_topics(recommendations)
                return cleaned[:max_recommendations]
            return []
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []