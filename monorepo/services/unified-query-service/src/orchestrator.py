"""
Query Orchestrator - Manages queries across multiple memory systems
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .models import QueryMode, MemorySource, QueryResult, QueryStats
from .adapters import (
    CogneeAdapter, MementoAdapter, 
    MemOSAdapter, LlamaCloudAdapter
)
from .ranking import RankingEngine
from .cache import QueryCache

logger = structlog.get_logger()


class QueryOrchestrator:
    """Orchestrates queries across multiple memory systems"""
    
    def __init__(self):
        self.adapters: Dict[str, 'MemorySystemAdapter'] = {}
        self.ranking_engine = RankingEngine()
        self.cache = QueryCache()
        self.stats = QueryStats()
        self._initialized = False
    
    async def initialize(self):
        """Initialize all memory system adapters"""
        logger.info("Initializing Query Orchestrator")
        
        # Initialize adapters based on configuration
        if "cognee" in settings.ENABLED_MEMORY_SYSTEMS:
            self.adapters["cognee"] = CogneeAdapter(settings.COGNEE_URL)
        
        if "memento" in settings.ENABLED_MEMORY_SYSTEMS:
            self.adapters["memento"] = MementoAdapter(settings.MEMENTO_URL)
        
        if "memos" in settings.ENABLED_MEMORY_SYSTEMS:
            self.adapters["memos"] = MemOSAdapter(settings.MEMOS_URL)
        
        if "llamacloud" in settings.ENABLED_MEMORY_SYSTEMS:
            self.adapters["llamacloud"] = LlamaCloudAdapter(settings.LLAMACLOUD_URL)
        
        # Initialize all adapters
        init_tasks = [adapter.initialize() for adapter in self.adapters.values()]
        await asyncio.gather(*init_tasks)
        
        self._initialized = True
        logger.info("Query Orchestrator initialized", 
                   adapters=list(self.adapters.keys()))
    
    async def shutdown(self):
        """Shutdown all adapters"""
        logger.info("Shutting down Query Orchestrator")
        
        shutdown_tasks = [adapter.shutdown() for adapter in self.adapters.values()]
        await asyncio.gather(*shutdown_tasks)
        
        self._initialized = False
    
    async def query(
        self,
        query: str,
        mode: QueryMode = QueryMode.SMART,
        sources: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a query across memory systems
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(query, mode, sources, options)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            self.stats.cache_hit_rate += 1
            return cached_result
        
        # Determine which sources to query
        if not sources:
            sources = list(self.adapters.keys())
        else:
            sources = [s for s in sources if s in self.adapters]
        
        # Execute query based on mode
        if mode == QueryMode.UNIFIED:
            results = await self._query_unified(query, sources, options)
        elif mode == QueryMode.SEQUENTIAL:
            results = await self._query_sequential(query, sources, options)
        elif mode == QueryMode.PARALLEL:
            results = await self._query_parallel(query, sources, options)
        else:  # SMART mode
            results = await self._query_smart(query, sources, options)
        
        # Process and rank results
        if mode != QueryMode.PARALLEL:
            results = await self._process_results(results, options)
        
        # Prepare response
        response = {
            "query": query,
            "mode": mode,
            "results": results,
            "total_results": len(results),
            "processing_time": time.time() - start_time,
            "sources_queried": sources,
            "metadata": {
                "cache_hit": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Cache the result
        await self.cache.set(cache_key, response)
        
        # Update statistics
        self._update_stats(mode, sources, time.time() - start_time)
        
        return response
    
    async def _query_unified(
        self, 
        query: str, 
        sources: List[str], 
        options: Dict[str, Any]
    ) -> List[QueryResult]:
        """Query all sources in parallel and merge results"""
        logger.debug("Executing unified query", query=query, sources=sources)
        
        # Create query tasks for all sources
        tasks = [
            self._query_single_source(source, query, options)
            for source in sources
        ]
        
        # Execute all queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and filter results
        all_results = []
        for source_results in results:
            if isinstance(source_results, Exception):
                logger.error("Source query failed", error=str(source_results))
                continue
            all_results.extend(source_results)
        
        return all_results
    
    async def _query_sequential(
        self,
        query: str,
        sources: List[str],
        options: Dict[str, Any]
    ) -> List[QueryResult]:
        """Query sources sequentially, using context from previous results"""
        logger.debug("Executing sequential query", query=query, sources=sources)
        
        all_results = []
        context = {}
        
        for source in sources:
            # Enhance query with context from previous results
            enhanced_query = self._enhance_query_with_context(query, context)
            
            # Query the source
            try:
                results = await self._query_single_source(
                    source, enhanced_query, options
                )
                all_results.extend(results)
                
                # Update context with new results
                context = self._update_context(context, results)
                
            except Exception as e:
                logger.error("Sequential query failed", 
                           source=source, error=str(e))
                continue
        
        return all_results
    
    async def _query_parallel(
        self,
        query: str,
        sources: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, List[QueryResult]]:
        """Query all sources in parallel, return grouped results"""
        logger.debug("Executing parallel query", query=query, sources=sources)
        
        # Create query tasks
        tasks = {
            source: self._query_single_source(source, query, options)
            for source in sources
        }
        
        # Execute in parallel
        results = await asyncio.gather(
            *[tasks[source] for source in sources],
            return_exceptions=True
        )
        
        # Group results by source
        grouped_results = {}
        for i, source in enumerate(sources):
            if isinstance(results[i], Exception):
                logger.error("Parallel query failed",
                           source=source, error=str(results[i]))
                grouped_results[source] = []
            else:
                grouped_results[source] = results[i]
        
        return grouped_results
    
    async def _query_smart(
        self,
        query: str,
        sources: List[str],
        options: Dict[str, Any]
    ) -> List[QueryResult]:
        """Intelligently route query based on analysis"""
        logger.debug("Executing smart query", query=query)
        
        # Analyze query to determine best approach
        analysis = await self.analyze_query(query)
        
        # Select sources based on analysis
        selected_sources = self._select_sources_for_query(analysis, sources)
        
        # Determine query mode based on analysis
        if analysis.get("requires_context", False):
            return await self._query_sequential(query, selected_sources, options)
        elif analysis.get("broad_search", False):
            return await self._query_unified(query, selected_sources, options)
        else:
            # Query most relevant source first
            primary_source = selected_sources[0]
            results = await self._query_single_source(
                primary_source, query, options
            )
            
            # If insufficient results, query additional sources
            if len(results) < options.get("max_results", 10):
                additional_results = await self._query_unified(
                    query, selected_sources[1:], options
                )
                results.extend(additional_results)
            
            return results
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _query_single_source(
        self,
        source: str,
        query: str,
        options: Dict[str, Any]
    ) -> List[QueryResult]:
        """Query a single memory source with retry logic"""
        adapter = self.adapters.get(source)
        if not adapter:
            logger.warning("Unknown source", source=source)
            return []
        
        config = settings.MEMORY_SYSTEM_CONFIG.get(source, {})
        timeout = config.get("timeout", 5.0)
        
        try:
            # Query with timeout
            results = await asyncio.wait_for(
                adapter.search(query, options),
                timeout=timeout
            )
            
            # Convert to QueryResult objects
            query_results = []
            for result in results:
                query_results.append(QueryResult(
                    id=result.get("id", ""),
                    content=result.get("content", ""),
                    source=source,
                    score=result.get("score", 0.0),
                    metadata=result.get("metadata", {}),
                    timestamp=datetime.utcnow(),
                    highlights=result.get("highlights")
                ))
            
            return query_results
            
        except asyncio.TimeoutError:
            logger.error("Query timeout", source=source, timeout=timeout)
            raise
        except Exception as e:
            logger.error("Query failed", source=source, error=str(e))
            raise
    
    async def _process_results(
        self,
        results: List[QueryResult],
        options: Dict[str, Any]
    ) -> List[QueryResult]:
        """Process, deduplicate, and rank results"""
        if not results:
            return []
        
        # Deduplicate if requested
        if options.get("deduplicate", True):
            results = self._deduplicate_results(results)
        
        # Rank results
        ranking_strategy = options.get("ranking_strategy", "hybrid")
        results = await self.ranking_engine.rank(
            results, 
            strategy=ranking_strategy,
            weights=settings.RANKING_WEIGHTS
        )
        
        # Limit results
        max_results = options.get("max_results", 10)
        return results[:max_results]
    
    def _deduplicate_results(
        self, 
        results: List[QueryResult]
    ) -> List[QueryResult]:
        """Remove duplicate results based on content similarity"""
        seen = set()
        unique_results = []
        
        for result in results:
            # Simple content hash for deduplication
            content_hash = hash(result.content.lower().strip())
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _enhance_query_with_context(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Enhance query with context from previous results"""
        if not context:
            return query
        
        # Extract key terms from context
        key_terms = context.get("key_terms", [])
        entities = context.get("entities", [])
        
        # Build enhanced query
        enhancements = []
        if key_terms:
            enhancements.append(f"Related to: {', '.join(key_terms[:5])}")
        if entities:
            enhancements.append(f"Involving: {', '.join(entities[:5])}")
        
        if enhancements:
            return f"{query} ({'; '.join(enhancements)})"
        
        return query
    
    def _update_context(
        self,
        context: Dict[str, Any],
        results: List[QueryResult]
    ) -> Dict[str, Any]:
        """Update context with information from new results"""
        # Extract key information from results
        for result in results[:5]:  # Use top 5 results
            # Extract entities, keywords, etc. from metadata
            metadata = result.metadata
            
            # Update key terms
            if "keywords" in metadata:
                context.setdefault("key_terms", []).extend(metadata["keywords"])
            
            # Update entities
            if "entities" in metadata:
                context.setdefault("entities", []).extend(metadata["entities"])
        
        # Deduplicate
        if "key_terms" in context:
            context["key_terms"] = list(set(context["key_terms"]))[:10]
        if "entities" in context:
            context["entities"] = list(set(context["entities"]))[:10]
        
        return context
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine optimal routing"""
        analysis = {
            "query_type": "general",
            "complexity": "simple",
            "requires_context": False,
            "broad_search": False,
            "recommended_sources": [],
            "features_needed": []
        }
        
        query_lower = query.lower()
        
        # Detect query type
        if any(term in query_lower for term in ["how", "why", "explain"]):
            analysis["query_type"] = "explanatory"
            analysis["requires_context"] = True
        elif any(term in query_lower for term in ["when", "date", "time"]):
            analysis["query_type"] = "temporal"
        elif any(term in query_lower for term in ["who", "person", "user"]):
            analysis["query_type"] = "entity"
        elif any(term in query_lower for term in ["document", "file", "pdf"]):
            analysis["query_type"] = "document"
        
        # Detect complexity
        if len(query.split()) > 10 or any(op in query for op in ["AND", "OR", "NOT"]):
            analysis["complexity"] = "complex"
            analysis["broad_search"] = True
        
        # Recommend sources based on query type
        if analysis["query_type"] == "explanatory":
            analysis["recommended_sources"] = ["cognee", "llamacloud"]
            analysis["features_needed"] = ["semantic_search", "concept_linking"]
        elif analysis["query_type"] == "document":
            analysis["recommended_sources"] = ["llamacloud", "memos"]
            analysis["features_needed"] = ["document_search", "structured_extraction"]
        elif analysis["query_type"] == "entity":
            analysis["recommended_sources"] = ["memos", "cognee"]
            analysis["features_needed"] = ["user_context", "graph_traversal"]
        else:
            analysis["recommended_sources"] = ["cognee", "llamacloud", "memos"]
            analysis["features_needed"] = ["semantic_search", "fast_retrieval"]
        
        # Set mode recommendation
        if analysis["requires_context"]:
            analysis["mode"] = QueryMode.SEQUENTIAL
        elif analysis["broad_search"]:
            analysis["mode"] = QueryMode.UNIFIED
        else:
            analysis["mode"] = QueryMode.SMART
        
        return analysis
    
    def _select_sources_for_query(
        self,
        analysis: Dict[str, Any],
        available_sources: List[str]
    ) -> List[str]:
        """Select best sources for query based on analysis"""
        recommended = analysis.get("recommended_sources", [])
        features_needed = analysis.get("features_needed", [])
        
        # Filter available sources
        selected = []
        
        # First, add recommended sources that are available
        for source in recommended:
            if source in available_sources and source in self.adapters:
                selected.append(source)
        
        # Then add other sources that have needed features
        for source, config in settings.MEMORY_SYSTEM_CONFIG.items():
            if source in available_sources and source not in selected:
                source_features = config.get("features", [])
                if any(feature in source_features for feature in features_needed):
                    selected.append(source)
        
        # If no sources selected, use all available
        if not selected:
            selected = available_sources
        
        return selected
    
    async def check_health(self) -> Dict[str, Any]:
        """Check health of all memory systems"""
        health_checks = []
        
        for name, adapter in self.adapters.items():
            start_time = time.time()
            try:
                is_healthy = await adapter.health_check()
                health_checks.append({
                    "name": name,
                    "status": "healthy" if is_healthy else "unhealthy",
                    "latency": time.time() - start_time,
                    "last_check": datetime.utcnow().isoformat()
                })
            except Exception as e:
                health_checks.append({
                    "name": name,
                    "status": "error",
                    "latency": time.time() - start_time,
                    "last_check": datetime.utcnow().isoformat(),
                    "error": str(e)
                })
        
        # Overall status
        healthy_count = sum(1 for h in health_checks if h["status"] == "healthy")
        overall_status = "healthy" if healthy_count > 0 else "unhealthy"
        
        return {
            "service": "unified-query-service",
            "status": overall_status,
            "version": "1.0.0",
            "systems": health_checks,
            "healthy_systems": healthy_count,
            "total_systems": len(health_checks)
        }
    
    def _generate_cache_key(
        self,
        query: str,
        mode: QueryMode,
        sources: Optional[List[str]],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for query"""
        sources_str = ",".join(sorted(sources or []))
        options_str = str(sorted(options.items())) if options else ""
        return f"{query}:{mode}:{sources_str}:{options_str}"
    
    def _update_stats(
        self,
        mode: QueryMode,
        sources: List[str],
        latency: float
    ):
        """Update query statistics"""
        self.stats.total_queries += 1
        
        # Update mode counts
        self.stats.queries_by_mode[mode] = \
            self.stats.queries_by_mode.get(mode, 0) + 1
        
        # Update source counts
        for source in sources:
            self.stats.queries_by_source[source] = \
                self.stats.queries_by_source.get(source, 0) + 1
        
        # Update average latency (simple moving average)
        self.stats.average_latency = (
            (self.stats.average_latency * (self.stats.total_queries - 1) + latency) /
            self.stats.total_queries
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        return self.stats.dict()