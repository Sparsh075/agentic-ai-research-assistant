# backend/storage/neo4j_store.py
from typing import List, Dict, Any, Optional
from app_logger.logger import get_logger

class Neo4jStore:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.logger = get_logger("neo4j-store")
            self.logger.info("Connected to Neo4j database")
        except ImportError:
            self.logger = get_logger("neo4j-store")
            self.logger.warning("Neo4j driver not available, using in-memory fallback")
            self.driver = None
            self.in_memory_graph = {}
            self.in_memory_relationships = []
        except Exception as e:
            self.logger = get_logger("neo4j-store")
            self.logger.warning(f"Neo4j connection failed: {e}, using in-memory fallback")
            self.driver = None
            self.in_memory_graph = {}
            self.in_memory_relationships = []

    def save_topics_and_relationships(self, graph):
        """Save graph data to Neo4j"""
        if self.driver:
            with self.driver.session() as session:
                # Save topics
                for topic, metadata in graph.topics.items():
                    session.run("""
                        MERGE (t:Topic {name: $name})
                        SET t += $metadata
                        """,
                        name=topic,
                        metadata=metadata
                    )

                # Save relationships
                for topic1, relationships in graph.graph.items():
                    for topic2, weight, rel_type in relationships:
                        session.run("""
                            MATCH (t1:Topic {name: $topic1})
                            MATCH (t2:Topic {name: $topic2})
                            MERGE (t1)-[r:RELATED {type: $rel_type}]->(t2)
                            SET r.weight = $weight
                            """,
                            topic1=topic1,
                            topic2=topic2,
                            rel_type=rel_type,
                            weight=weight
                        )
        else:
            # Fallback: store in memory
            self.in_memory_graph = dict(graph.graph)
            self.logger.debug("Stored graph data in memory (Neo4j not available)")

    def load_graph(self, graph):
        """Load graph data from Neo4j"""
        if self.driver:
            with self.driver.session() as session:
                # Load topics
                result = session.run("MATCH (t:Topic) RETURN t.name as name, t as properties")
                for record in result:
                    name = record["name"]
                    properties = dict(record["properties"])
                    properties.pop("name", None)  # Remove name from properties
                    graph.add_topic(name, properties)

                # Load relationships
                result = session.run("""
                    MATCH (t1:Topic)-[r:RELATED]->(t2:Topic)
                    RETURN t1.name as topic1, t2.name as topic2, r.weight as weight, r.type as rel_type
                    """)
                for record in result:
                    graph.add_relationship(
                        record["topic1"],
                        record["topic2"],
                        record["weight"],
                        record["rel_type"]
                    )
        else:
            # Load from memory
            graph.graph = self.in_memory_graph.copy()
            self.logger.debug("Loaded graph data from memory")

    def get_related_topics(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get related topics from database"""
        if self.driver:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Topic {name: $topic})-[r:RELATED]-(related:Topic)
                    RETURN related.name as name, r.weight as weight, r.type as rel_type
                    ORDER BY r.weight DESC
                    LIMIT $limit
                    """,
                    topic=topic,
                    limit=limit
                )
                return [{"name": r["name"], "weight": r["weight"], "type": r["rel_type"]} for r in result]
        else:
            # Fallback
            return []

    def search_topics(self, query: str, limit: int = 10) -> List[str]:
        """Search for topics matching query"""
        if self.driver:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Topic)
                    WHERE t.name CONTAINS $query OR t.description CONTAINS $query
                    RETURN t.name as name
                    LIMIT $limit
                    """,
                    query=query,
                    limit=limit
                )
                return [r["name"] for r in result]
        else:
            # Fallback search
            return [topic for topic in self.in_memory_graph.keys() if query.lower() in topic.lower()][:limit]

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()