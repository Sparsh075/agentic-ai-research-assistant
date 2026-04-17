# backend/dsa/trie.py
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.topics = []  # List of topics that end here

class TopicTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, topic):
        node = self.root
        for char in topic.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.topics.append(topic)

    def autocomplete(self, prefix, max_results=10):
        """Get autocomplete suggestions"""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all topics from this node
        results = []
        self._collect_topics(node, prefix.lower(), results, max_results)
        return results[:max_results]

    def _collect_topics(self, node, current_prefix, results, max_results):
        if len(results) >= max_results:
            return

        if node.is_end_of_word:
            results.extend(node.topics)

        for char, child_node in node.children.items():
            if len(results) < max_results:
                self._collect_topics(child_node, current_prefix + char, results, max_results)

    def search(self, word):
        """Check if word exists in trie"""
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word