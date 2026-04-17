#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from utils.topic_extractor import TopicExtractor
    print("✅ TopicExtractor import successful")

    # Test basic functionality
    extractor = TopicExtractor()
    print("✅ TopicExtractor instantiation successful")

    # Test normalize_topics method
    test_topics = ["Dynamic Programming", "Graph Algorithms", "Machine Learning", "Data Structures"]
    normalized = extractor._normalize_topics(test_topics)
    print(f"✅ Normalization test: {normalized}")

    print("🎉 All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()