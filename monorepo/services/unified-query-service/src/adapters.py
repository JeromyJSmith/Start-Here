"""
Memory System Adapters - Interfaces to different memory systems
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
import asyncio

import structlog

logger = structlog.get_logger()


class MemorySystemAdapter(ABC):
    """Base adapter for memory systems"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the adapter"""
        self._initialized = True
        logger.info(f"Initialized {self.__class__.__name__}", url=self.base_url)
    
    async def shutdown(self):
        """Shutdown the adapter"""
        await self.client.aclose()
        self._initialized = False
    
    @abstractmethod
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search the memory system"""
        pass
    
    @abstractmethod
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content in the memory system"""
        pass
    
    async def health_check(self) -> bool:
        """Check if the memory system is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {self.__class__.__name__}", 
                        error=str(e))
            return False


class CogneeAdapter(MemorySystemAdapter):
    """Adapter for Cognee semantic memory system"""
    
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Cognee's semantic graph"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/search",
                json={
                    "query": query,
                    "limit": options.get("max_results", 10),
                    "include_graph": True,
                    "semantic_search": True
                }
            )
            response.raise_for_status()
            
            results = response.json().get("results", [])
            
            # Transform Cognee results to standard format
            transformed = []
            for result in results:
                transformed.append({
                    "id": result.get("id"),
                    "content": result.get("content", ""),
                    "score": result.get("similarity_score", 0.0),
                    "metadata": {
                        "source": "cognee",
                        "graph_depth": result.get("graph_depth", 0),
                        "entities": result.get("entities", []),
                        "relationships": result.get("relationships", []),
                        "keywords": result.get("keywords", [])
                    },
                    "highlights": result.get("highlights", [])
                })
            
            return transformed
            
        except Exception as e:
            logger.error("Cognee search failed", query=query, error=str(e))
            return []
    
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content in Cognee"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/add",
                json={
                    "content": content,
                    "metadata": metadata,
                    "process_graph": True
                }
            )
            response.raise_for_status()
            
            return response.json().get("id", "")
            
        except Exception as e:
            logger.error("Cognee store failed", error=str(e))
            raise


class MementoAdapter(MemorySystemAdapter):
    """Adapter for Memento MCP key-value memory"""
    
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Memento's key-value store"""
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "limit": options.get("max_results", 10)
                }
            )
            response.raise_for_status()
            
            results = response.json().get("memories", [])
            
            # Transform Memento results
            transformed = []
            for result in results:
                transformed.append({
                    "id": result.get("key"),
                    "content": result.get("value", ""),
                    "score": result.get("relevance", 0.0),
                    "metadata": {
                        "source": "memento",
                        "timestamp": result.get("timestamp"),
                        "tags": result.get("tags", [])
                    }
                })
            
            return transformed
            
        except Exception as e:
            logger.error("Memento search failed", query=query, error=str(e))
            return []
    
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content in Memento"""
        try:
            key = metadata.get("key", f"memory_{hash(content)}")
            
            response = await self.client.post(
                f"{self.base_url}/store",
                json={
                    "key": key,
                    "value": content,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            
            return key
            
        except Exception as e:
            logger.error("Memento store failed", error=str(e))
            raise


class MemOSAdapter(MemorySystemAdapter):
    """Adapter for MemOS multi-type memory system"""
    
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search MemOS memory cubes"""
        try:
            user_id = options.get("user_id", "default")
            
            response = await self.client.post(
                f"{self.base_url}/api/search",
                json={
                    "query": query,
                    "user_id": user_id,
                    "limit": options.get("max_results", 10),
                    "memory_types": ["text_mem", "act_mem"]
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process text memories
            for mem in data.get("text_mem", []):
                results.append({
                    "id": mem.get("id"),
                    "content": mem.get("content", ""),
                    "score": mem.get("score", 0.0),
                    "metadata": {
                        "source": "memos",
                        "memory_type": "text",
                        "user_id": user_id,
                        "cube_id": mem.get("cube_id"),
                        "timestamp": mem.get("timestamp")
                    }
                })
            
            # Process activation memories if any
            for mem in data.get("act_mem", []):
                results.append({
                    "id": mem.get("id"),
                    "content": mem.get("summary", ""),
                    "score": mem.get("score", 0.0),
                    "metadata": {
                        "source": "memos",
                        "memory_type": "activation",
                        "kv_cache": mem.get("kv_data"),
                        "context_length": mem.get("context_length")
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error("MemOS search failed", query=query, error=str(e))
            return []
    
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content in MemOS"""
        try:
            user_id = metadata.get("user_id", "default")
            
            response = await self.client.post(
                f"{self.base_url}/api/add",
                json={
                    "messages": [
                        {"role": "system", "content": content}
                    ],
                    "user_id": user_id,
                    "metadata": metadata
                }
            )
            response.raise_for_status()
            
            return response.json().get("memory_id", "")
            
        except Exception as e:
            logger.error("MemOS store failed", error=str(e))
            raise


class LlamaCloudAdapter(MemorySystemAdapter):
    """Adapter for LlamaCloud document index"""
    
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search LlamaCloud indexes"""
        try:
            # Use MCP interface for LlamaCloud
            response = await self.client.post(
                f"{self.base_url}/mcp/tools/query_main-docs",
                json={
                    "query": query,
                    "top_k": options.get("max_results", 10),
                    "filters": options.get("filters", {})
                },
                headers={
                    "Authorization": f"Bearer {options.get('api_key', '')}"
                }
            )
            response.raise_for_status()
            
            results = response.json().get("results", [])
            
            # Transform LlamaCloud results
            transformed = []
            for result in results:
                transformed.append({
                    "id": result.get("doc_id"),
                    "content": result.get("text", ""),
                    "score": result.get("score", 0.0),
                    "metadata": {
                        "source": "llamacloud",
                        "document_name": result.get("document_name"),
                        "page": result.get("page"),
                        "chunk_id": result.get("chunk_id"),
                        "index_name": result.get("index_name", "main-docs")
                    },
                    "highlights": result.get("highlights", [])
                })
            
            return transformed
            
        except Exception as e:
            logger.error("LlamaCloud search failed", query=query, error=str(e))
            return []
    
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store document in LlamaCloud"""
        try:
            # LlamaCloud typically ingests documents through pipelines
            # This would integrate with LlamaParse
            response = await self.client.post(
                f"{self.base_url}/api/ingest",
                json={
                    "content": content,
                    "metadata": metadata,
                    "index_name": metadata.get("index_name", "main-docs")
                }
            )
            response.raise_for_status()
            
            return response.json().get("document_id", "")
            
        except Exception as e:
            logger.error("LlamaCloud store failed", error=str(e))
            raise