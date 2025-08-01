#!/usr/bin/env python3
"""
Memory Integration Service
Combines Cognee's graph memory with Memento MCP's knowledge graph
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Cognee imports
import cognee
from cognee import add, search, prune

# Neo4j connection
from neo4j import AsyncGraphDatabase

class MemoryIntegrationService:
    """Integrates Cognee and Memento MCP for unified memory operations"""
    
    def __init__(self):
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "development")
        self.driver = None
        
    async def initialize(self):
        """Initialize the memory service"""
        # Initialize Neo4j driver
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Initialize Cognee
        await cognee.prune.prune_system()
        print("Memory Integration Service initialized")
        
    async def close(self):
        """Close connections"""
        if self.driver:
            await self.driver.close()
    
    async def add_memory(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add content to both Cognee and create corresponding entities in Neo4j
        
        Args:
            content: Text content to remember
            metadata: Optional metadata about the content
            
        Returns:
            Dict with status and created entities
        """
        try:
            # Add to Cognee for semantic processing
            await add(content)
            
            # Extract entities and relations using Cognee
            cognee_results = await search(content)
            
            # Create entities in Neo4j for Memento MCP
            entities_created = []
            relations_created = []
            
            async with self.driver.session() as session:
                # Create entities from Cognee results
                for item in cognee_results:
                    if item.get("type") == "entity":
                        entity_name = item.get("name", "").replace(" ", "_")
                        entity_type = item.get("entity_type", "general")
                        observations = [content] if entity_name.lower() in content.lower() else []
                        
                        # Create entity node
                        query = """
                        MERGE (e:Entity {name: $name})
                        SET e.entityType = $entityType,
                            e.observations = $observations,
                            e.createdAt = timestamp(),
                            e.updatedAt = timestamp()
                        RETURN e
                        """
                        
                        result = await session.run(
                            query,
                            name=entity_name,
                            entityType=entity_type,
                            observations=observations
                        )
                        
                        entities_created.append({
                            "name": entity_name,
                            "type": entity_type
                        })
                
                # Create relations from Cognee results
                for item in cognee_results:
                    if item.get("type") == "relation":
                        from_entity = item.get("from", "").replace(" ", "_")
                        to_entity = item.get("to", "").replace(" ", "_")
                        relation_type = item.get("relation_type", "related_to")
                        
                        # Create relation
                        query = """
                        MATCH (from:Entity {name: $from})
                        MATCH (to:Entity {name: $to})
                        CREATE (from)-[r:RELATES_TO {
                            relationType: $relationType,
                            strength: $strength,
                            confidence: $confidence,
                            createdAt: timestamp()
                        }]->(to)
                        RETURN r
                        """
                        
                        result = await session.run(
                            query,
                            from=from_entity,
                            to=to_entity,
                            relationType=relation_type,
                            strength=0.8,
                            confidence=0.9
                        )
                        
                        relations_created.append({
                            "from": from_entity,
                            "to": to_entity,
                            "type": relation_type
                        })
            
            return {
                "status": "success",
                "entities": entities_created,
                "relations": relations_created,
                "cognee_results": len(cognee_results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def search_memory(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search memories using both Cognee and Neo4j
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Combined search results
        """
        try:
            # Search using Cognee
            cognee_results = await search(query)
            
            # Search using Neo4j vector similarity
            neo4j_results = []
            async with self.driver.session() as session:
                # Text search in Neo4j
                query_cypher = """
                MATCH (e:Entity)
                WHERE e.name CONTAINS $query 
                   OR ANY(obs IN e.observations WHERE obs CONTAINS $query)
                RETURN e
                LIMIT $limit
                """
                
                result = await session.run(
                    query_cypher,
                    query=query,
                    limit=limit
                )
                
                async for record in result:
                    entity = record["e"]
                    neo4j_results.append({
                        "name": entity["name"],
                        "type": entity.get("entityType", "unknown"),
                        "observations": entity.get("observations", [])
                    })
            
            return {
                "status": "success",
                "cognee_results": cognee_results,
                "neo4j_results": neo4j_results,
                "total_results": len(cognee_results) + len(neo4j_results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_knowledge_graph(self) -> Dict[str, Any]:
        """
        Get the full knowledge graph from Neo4j
        
        Returns:
            Graph structure with nodes and edges
        """
        try:
            nodes = []
            edges = []
            
            async with self.driver.session() as session:
                # Get all entities
                node_query = """
                MATCH (e:Entity)
                RETURN e
                """
                
                result = await session.run(node_query)
                async for record in result:
                    entity = record["e"]
                    nodes.append({
                        "id": entity["name"],
                        "label": entity["name"],
                        "type": entity.get("entityType", "unknown"),
                        "observations": entity.get("observations", [])
                    })
                
                # Get all relations
                edge_query = """
                MATCH (from:Entity)-[r:RELATES_TO]->(to:Entity)
                RETURN from.name as from, to.name as to, r
                """
                
                result = await session.run(edge_query)
                async for record in result:
                    edges.append({
                        "from": record["from"],
                        "to": record["to"],
                        "type": record["r"].get("relationType", "related_to"),
                        "strength": record["r"].get("strength", 0.5),
                        "confidence": record["r"].get("confidence", 0.5)
                    })
            
            return {
                "status": "success",
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Example usage and API endpoints
async def main():
    """Example usage of the memory integration service"""
    service = MemoryIntegrationService()
    await service.initialize()
    
    # Add some memories
    result = await service.add_memory(
        "Claude Code is a powerful AI assistant that helps with software development. "
        "It integrates with Neo4j for graph-based memory storage."
    )
    print("Add memory result:", result)
    
    # Search memories
    search_result = await service.search_memory("Claude Code")
    print("Search result:", search_result)
    
    # Get knowledge graph
    graph = await service.get_knowledge_graph()
    print("Knowledge graph:", graph)
    
    await service.close()


if __name__ == "__main__":
    asyncio.run(main())