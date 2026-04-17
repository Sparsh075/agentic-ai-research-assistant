# backend/utils/topic_extractor.py
from typing import List, Dict
import re

from ..engines.ai_engine import AIEngine
from ..app_logger.logger import get_logger

class TopicExtractor:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.logger = get_logger("topic-extractor")

    def extract_topics(self, user_query: str, ai_response: str) -> List[str]:
        """Extract 3-5 clean, meaningful technical topics using AI."""
        topics = self.ai_engine.extract_topics_from_response(user_query, ai_response)
        return self._normalize_topics(topics)

    def _normalize_topics(self, topics: List[str]) -> List[str]:
        """Clean and deduplicate topic strings, ensure 3-5 short topics."""
        cleaned = []
        seen = set()

        for raw in topics:
            if not isinstance(raw, str):
                continue
            topic = raw.strip().lower()
            topic = re.sub(r'[^a-z0-9 ]+', ' ', topic)
            topic = re.sub(r'\s{2,}', ' ', topic).strip()
            words = topic.split()
            if len(words) > 3:
                topic = ' '.join(words[:3])
            if not topic or len(topic) < 3 or topic in seen:
                continue
            seen.add(topic)
            cleaned.append(topic)
            if len(cleaned) >= 5:
                break

        # Ensure at least 3 topics
        while len(cleaned) < 3 and len(cleaned) < len(topics):
            for raw in topics[len(cleaned):]:
                if isinstance(raw, str):
                    topic = raw.strip().lower()[:20]  # Shorten
                    if topic not in seen:
                        cleaned.append(topic)
                        seen.add(topic)
                        if len(cleaned) >= 3:
                            break

        return cleaned[:5]