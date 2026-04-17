# backend/engines/ai_engine.py
from typing import List, Dict, Any, Optional
from ..llm.llm_router import generate_response
from ..app_logger.logger import get_logger

class AIEngine:
    def __init__(self):
        self.logger = get_logger("ai-engine")

    def process_query(self, query: str, context: Optional[str] = None, model: Optional[str] = None) -> str:
        """Process user query with optional context"""
        if context:
            enhanced_prompt = f"""
Context from knowledge graph: {context}

User Query: {query}

Provide a comprehensive answer using the context above when relevant.
"""
        else:
            enhanced_prompt = query

        try:
            response = generate_response(enhanced_prompt, model=model)
            self.logger.info(f"Generated response for query: {query[:50]}...")
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your query."

    def _parse_json_array(self, response: str) -> List[str]:
        import json
        import re

        text = response.strip()
        match = re.search(r'\[.*\]', text, flags=re.S)
        if match:
            text = match.group(0)

        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON array from LLM response")
            return []

    def extract_topics_from_response(self, user_query: str, ai_response: str) -> List[str]:
        """Extract topics from AI response using LLM"""
        prompt = f"""
Analyze the following user query and AI response. Extract 3-5 key topics/concepts that should be added to a knowledge graph.

Focus on:
- Technical concepts
- Domain-specific terms
- Related technologies
- Prerequisites or related topics

Return only a JSON array of 3-5 topic strings, with no explanation.

User Query: {user_query}
AI Response: {ai_response}

Topics:"""

        try:
            raw_response = generate_response(prompt, model="llama3:8b", options={"max_tokens": 200})
            topics = self._parse_json_array(raw_response)
            cleaned = []
            seen = set()
            for topic in topics:
                if not isinstance(topic, str):
                    continue
                t = topic.strip().lower()
                t = t.split('\n')[0].strip()
                t = re.sub(r'^(explain|what is|how to|tell me about|describe)\s+', '', t)
                t = re.sub(r'\s+(with|using|that|which|because|for|to|by|as|is|are|was|were|be|been|being)\b.*$', '', t)
                t = t.replace('`', '').strip(' .,:;"')
                t = re.sub(r'\b(the|a|an|and|or|of|for|to|in|on)\b', '', t)
                t = re.sub(r'\s{2,}', ' ', t).strip()
                if not t or len(t) < 4:
                    continue
                if len(t.split()) > 4:
                    t = ' '.join(t.split()[:4])
                if any(stop in t for stop in ['with the hope', 'here is', 'response', 'example', 'procedure']):
                    continue
                if t in seen:
                    continue
                seen.add(t)
                cleaned.append(t)
                if len(cleaned) >= 5:
                    break
            if len(cleaned) >= 3:
                return cleaned[:5]
            return self._extract_fallback_topics(user_query + '\n' + ai_response)
        except Exception as e:
            self.logger.error(f"Error extracting topics: {e}")
            return self._extract_fallback_topics(user_query + '\n' + ai_response)

    def generate_recommendations(self, current_topic: str) -> List[str]:
        """Generate topic recommendations using LLM"""
        prompt = f"""
Based on the topic "{current_topic}", suggest 5 related topics that users might want to explore next.
Consider prerequisites, advanced concepts, and related technologies.

Return only a JSON array of 5 topic strings.
"""

        try:
            raw_response = generate_response(prompt, model="llama3:8b", options={"max_tokens": 150})
            recommendations = self._parse_json_array(raw_response)
            return [rec.lower().strip() for rec in recommendations if isinstance(rec, str) and rec.strip()]
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []

    def _extract_fallback_topics(self, text: str) -> List[str]:
        """Fallback topic extraction using regex"""
        import re
        # Extract capitalized words and technical terms
        patterns = [
            r'\b[A-Z][a-zA-Z\s]{2,}\b',  # Capitalized phrases
            r'\b[a-zA-Z]+(?:\s+[a-zA-Z]+)*\b'  # Multi-word terms
        ]

        topics = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match.split()) >= 2 and len(match) > 3:
                    topics.add(match.lower().strip())

        return list(topics)[:10]