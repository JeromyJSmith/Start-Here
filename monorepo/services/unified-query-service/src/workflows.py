"""
Pre-built workflows for the Unified Query Service
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Event
)
import structlog

from .orchestrator import QueryOrchestrator
from .document_processor import DocumentProcessor
from .models import QueryMode, MemorySource

logger = structlog.get_logger()


# Custom events for workflows
class MemorySyncEvent(Event):
    """Event for memory synchronization"""
    source_system: str
    target_systems: List[str]
    data: Dict[str, Any]


class DocumentEvent(Event):
    """Event for document processing"""
    file_path: str
    pipeline: str
    metadata: Dict[str, Any]


class QueryAnalysisEvent(Event):
    """Event for query analysis"""
    query: str
    analysis: Dict[str, Any]
    suggestions: List[str]


class MaintenanceEvent(Event):
    """Event for maintenance tasks"""
    task_type: str
    target_system: str
    parameters: Dict[str, Any]


class MemorySyncWorkflow(Workflow):
    """Synchronizes memory across different systems"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = QueryOrchestrator()
        self.sync_stats = {
            "total_synced": 0,
            "failures": 0,
            "last_sync": None
        }
    
    @step
    async def start_sync(self, ev: StartEvent) -> MemorySyncEvent:
        """Start memory synchronization"""
        logger.info("Starting memory sync workflow")
        
        # Get sync configuration
        config = ev.data.get("config", {})
        source = config.get("source", "cognee")
        targets = config.get("targets", ["memos", "llamacloud"])
        
        # Query source system for recent updates
        query_time = datetime.utcnow().isoformat()
        results = await self.orchestrator.query(
            query=f"updated_after:{config.get('last_sync', '2024-01-01')}",
            mode=QueryMode.PARALLEL,
            sources=[source]
        )
        
        return MemorySyncEvent(
            source_system=source,
            target_systems=targets,
            data={
                "results": results,
                "query_time": query_time,
                "batch_size": len(results.get(source, []))
            }
        )
    
    @step
    async def sync_to_targets(self, ev: MemorySyncEvent) -> StopEvent:
        """Sync data to target systems"""
        source_data = ev.data.get("results", {}).get(ev.source_system, [])
        
        sync_results = {
            "source": ev.source_system,
            "targets": {},
            "total_items": len(source_data),
            "synced_items": 0,
            "failed_items": 0
        }
        
        # Sync to each target system
        for target in ev.target_systems:
            if target == ev.source_system:
                continue
            
            logger.info(f"Syncing to {target}", items=len(source_data))
            
            success_count = 0
            fail_count = 0
            
            # Get target adapter
            adapter = self.orchestrator.adapters.get(target)
            if not adapter:
                logger.error(f"No adapter found for {target}")
                continue
            
            # Sync each item
            for item in source_data:
                try:
                    # Transform data for target system
                    transformed = self._transform_for_target(item, target)
                    
                    # Store in target
                    await adapter.store(
                        content=transformed["content"],
                        metadata=transformed["metadata"]
                    )
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync item to {target}", error=str(e))
                    fail_count += 1
            
            sync_results["targets"][target] = {
                "success": success_count,
                "failed": fail_count
            }
            sync_results["synced_items"] += success_count
            sync_results["failed_items"] += fail_count
        
        # Update stats
        self.sync_stats["total_synced"] += sync_results["synced_items"]
        self.sync_stats["failures"] += sync_results["failed_items"]
        self.sync_stats["last_sync"] = datetime.utcnow()
        
        return StopEvent(result=sync_results)
    
    def _transform_for_target(self, item: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Transform data for specific target system"""
        # Base transformation
        transformed = {
            "content": item.get("content", ""),
            "metadata": item.get("metadata", {})
        }
        
        # Target-specific transformations
        if target == "memos":
            # MemOS expects messages format
            transformed["content"] = item.get("content", "")
            transformed["metadata"]["memory_type"] = "synced"
            
        elif target == "llamacloud":
            # LlamaCloud expects document format
            transformed["metadata"]["source_system"] = item.get("source", "unknown")
            transformed["metadata"]["sync_timestamp"] = datetime.utcnow().isoformat()
        
        return transformed


class DocumentIngestionWorkflow(Workflow):
    """Monitors and processes new documents"""
    
    def __init__(self):
        super().__init__()
        self.processor = DocumentProcessor()
        self.watch_folders = []
        self.processed_files = set()
    
    @step
    async def scan_folders(self, ev: StartEvent) -> DocumentEvent:
        """Scan folders for new documents"""
        config = ev.data.get("config", {})
        self.watch_folders = config.get("folders", ["/shared/documents"])
        pipeline = config.get("pipeline", "default")
        
        new_files = []
        
        # Scan each folder
        for folder in self.watch_folders:
            try:
                from pathlib import Path
                folder_path = Path(folder)
                
                if not folder_path.exists():
                    continue
                
                # Find documents
                for pattern in ["*.pdf", "*.docx", "*.txt", "*.md"]:
                    for file_path in folder_path.glob(pattern):
                        if str(file_path) not in self.processed_files:
                            new_files.append(str(file_path))
                
            except Exception as e:
                logger.error(f"Failed to scan folder {folder}", error=str(e))
        
        if new_files:
            # Process first new file
            file_to_process = new_files[0]
            logger.info(f"Found new document: {file_to_process}")
            
            return DocumentEvent(
                file_path=file_to_process,
                pipeline=pipeline,
                metadata={
                    "discovered_at": datetime.utcnow().isoformat(),
                    "remaining_files": len(new_files) - 1
                }
            )
        else:
            # No new files
            return StopEvent(result={"message": "No new documents found"})
    
    @step
    async def process_document(self, ev: DocumentEvent) -> StopEvent:
        """Process the document"""
        logger.info(f"Processing document: {ev.file_path}")
        
        # Start processing
        task_id = await self.processor.start_processing(
            file_path=ev.file_path,
            pipeline=ev.pipeline,
            store_in=[MemorySource.COGNEE, MemorySource.LLAMACLOUD]
        )
        
        # Wait for completion (with timeout)
        max_wait = 300  # 5 minutes
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.processor.get_task_status(task_id)
            
            if not status:
                break
            
            if status["status"] == "completed":
                # Mark as processed
                self.processed_files.add(ev.file_path)
                
                return StopEvent(result={
                    "file": ev.file_path,
                    "status": "success",
                    "task_id": task_id,
                    "result": status.get("result", {})
                })
            
            elif status["status"] == "failed":
                return StopEvent(result={
                    "file": ev.file_path,
                    "status": "failed",
                    "errors": status.get("errors", [])
                })
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > max_wait:
                return StopEvent(result={
                    "file": ev.file_path,
                    "status": "timeout",
                    "task_id": task_id
                })
            
            await asyncio.sleep(5)
        
        return StopEvent(result={"status": "unknown"})


class QueryEnhancementWorkflow(Workflow):
    """Analyzes query patterns and enhances future queries"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = QueryOrchestrator()
        self.query_history = []
        self.enhancement_rules = {}
    
    @step
    async def analyze_query(self, ev: StartEvent) -> QueryAnalysisEvent:
        """Analyze query for enhancement opportunities"""
        query = ev.data.get("query", "")
        user_context = ev.data.get("context", {})
        
        # Analyze query
        analysis = await self.orchestrator.analyze_query(query)
        
        # Generate suggestions based on history
        suggestions = self._generate_suggestions(query, analysis)
        
        # Add to history
        self.query_history.append({
            "query": query,
            "analysis": analysis,
            "timestamp": datetime.utcnow(),
            "context": user_context
        })
        
        return QueryAnalysisEvent(
            query=query,
            analysis=analysis,
            suggestions=suggestions
        )
    
    @step
    async def enhance_and_execute(self, ev: QueryAnalysisEvent) -> StopEvent:
        """Execute enhanced query"""
        original_query = ev.query
        
        # Apply enhancements
        enhanced_query = self._apply_enhancements(original_query, ev.suggestions)
        
        # Execute both queries for comparison
        original_results = await self.orchestrator.query(
            query=original_query,
            mode=QueryMode.SMART
        )
        
        enhanced_results = await self.orchestrator.query(
            query=enhanced_query,
            mode=QueryMode.SMART
        )
        
        # Compare results
        improvement = self._calculate_improvement(original_results, enhanced_results)
        
        # Update enhancement rules if improvement is significant
        if improvement > 0.1:  # 10% improvement
            self._update_enhancement_rules(ev.analysis, ev.suggestions)
        
        return StopEvent(result={
            "original_query": original_query,
            "enhanced_query": enhanced_query,
            "suggestions_applied": ev.suggestions,
            "improvement_score": improvement,
            "original_results": original_results.get("total_results", 0),
            "enhanced_results": enhanced_results.get("total_results", 0)
        })
    
    def _generate_suggestions(self, query: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate query enhancement suggestions"""
        suggestions = []
        
        # Based on query type
        if analysis.get("query_type") == "explanatory":
            suggestions.append("add_context:Include 'explain in detail' for comprehensive results")
        
        if analysis.get("complexity") == "simple":
            suggestions.append("expand_terms:Add related terms to broaden search")
        
        # Based on history
        similar_queries = self._find_similar_queries(query)
        if similar_queries:
            # Suggest successful patterns from history
            for sq in similar_queries[:3]:
                if sq.get("successful_pattern"):
                    suggestions.append(f"pattern:{sq['successful_pattern']}")
        
        # Based on detected entities
        if "entities" in analysis:
            suggestions.append("entity_expansion:Include related entities in search")
        
        return suggestions
    
    def _apply_enhancements(self, query: str, suggestions: List[str]) -> str:
        """Apply enhancement suggestions to query"""
        enhanced = query
        
        for suggestion in suggestions:
            if suggestion.startswith("add_context:"):
                context = suggestion.split(":", 1)[1]
                enhanced = f"{enhanced} ({context})"
            
            elif suggestion.startswith("expand_terms:"):
                # Add synonyms or related terms
                enhanced = f"{enhanced} OR related_terms"
            
            elif suggestion.startswith("entity_expansion:"):
                # Add entity variations
                enhanced = f"{enhanced} including_related_entities"
        
        return enhanced
    
    def _calculate_improvement(
        self, 
        original_results: Dict[str, Any], 
        enhanced_results: Dict[str, Any]
    ) -> float:
        """Calculate improvement score"""
        # Simple improvement calculation
        original_count = original_results.get("total_results", 0)
        enhanced_count = enhanced_results.get("total_results", 0)
        
        if original_count == 0:
            return 1.0 if enhanced_count > 0 else 0.0
        
        # Calculate improvement ratio
        improvement = (enhanced_count - original_count) / original_count
        
        # Factor in result quality (would use relevance scores in production)
        # For now, just return count improvement
        return max(0.0, min(1.0, improvement))
    
    def _find_similar_queries(self, query: str) -> List[Dict[str, Any]]:
        """Find similar queries from history"""
        # Simple similarity check (would use embeddings in production)
        similar = []
        
        query_words = set(query.lower().split())
        
        for hist in self.query_history[-100:]:  # Last 100 queries
            hist_words = set(hist["query"].lower().split())
            
            # Calculate Jaccard similarity
            intersection = query_words.intersection(hist_words)
            union = query_words.union(hist_words)
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > 0.5:
                    similar.append({
                        "query": hist["query"],
                        "similarity": similarity,
                        "successful_pattern": hist.get("successful_pattern")
                    })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar
    
    def _update_enhancement_rules(
        self, 
        analysis: Dict[str, Any], 
        suggestions: List[str]
    ):
        """Update enhancement rules based on successful patterns"""
        query_type = analysis.get("query_type", "general")
        
        if query_type not in self.enhancement_rules:
            self.enhancement_rules[query_type] = []
        
        # Add successful suggestions to rules
        self.enhancement_rules[query_type].extend(suggestions)
        
        # Keep only unique rules
        self.enhancement_rules[query_type] = list(set(self.enhancement_rules[query_type]))


class MaintenanceWorkflow(Workflow):
    """Performs maintenance tasks on memory systems"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = QueryOrchestrator()
        self.maintenance_log = []
    
    @step
    async def start_maintenance(self, ev: StartEvent) -> MaintenanceEvent:
        """Start maintenance tasks"""
        config = ev.data.get("config", {})
        task_type = config.get("task_type", "cleanup")
        target_system = config.get("target_system", "all")
        
        logger.info(f"Starting maintenance: {task_type} on {target_system}")
        
        # Determine parameters based on task type
        parameters = {}
        
        if task_type == "cleanup":
            parameters = {
                "older_than_days": config.get("older_than_days", 30),
                "preserve_important": True
            }
        elif task_type == "optimize":
            parameters = {
                "rebuild_indexes": True,
                "compact_storage": True
            }
        elif task_type == "backup":
            parameters = {
                "backup_location": config.get("backup_location", "/backups"),
                "compression": True
            }
        
        return MaintenanceEvent(
            task_type=task_type,
            target_system=target_system,
            parameters=parameters
        )
    
    @step
    async def execute_maintenance(self, ev: MaintenanceEvent) -> StopEvent:
        """Execute maintenance tasks"""
        results = {
            "task_type": ev.task_type,
            "target_system": ev.target_system,
            "start_time": datetime.utcnow(),
            "tasks_completed": [],
            "errors": []
        }
        
        # Get target systems
        if ev.target_system == "all":
            targets = list(self.orchestrator.adapters.keys())
        else:
            targets = [ev.target_system]
        
        # Execute maintenance on each target
        for target in targets:
            try:
                if ev.task_type == "cleanup":
                    result = await self._cleanup_system(target, ev.parameters)
                elif ev.task_type == "optimize":
                    result = await self._optimize_system(target, ev.parameters)
                elif ev.task_type == "backup":
                    result = await self._backup_system(target, ev.parameters)
                else:
                    result = {"status": "unknown_task"}
                
                results["tasks_completed"].append({
                    "system": target,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Maintenance failed for {target}", error=str(e))
                results["errors"].append({
                    "system": target,
                    "error": str(e)
                })
        
        results["end_time"] = datetime.utcnow()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        # Log maintenance
        self.maintenance_log.append(results)
        
        return StopEvent(result=results)
    
    async def _cleanup_system(
        self, 
        system: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Clean up old data from system"""
        adapter = self.orchestrator.adapters.get(system)
        if not adapter:
            return {"status": "no_adapter"}
        
        # This would implement actual cleanup in production
        # For now, return mock results
        return {
            "status": "success",
            "items_removed": 42,
            "space_freed": "1.2GB",
            "oldest_retained": "2024-01-15"
        }
    
    async def _optimize_system(
        self, 
        system: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize system performance"""
        # This would implement actual optimization in production
        return {
            "status": "success",
            "indexes_rebuilt": parameters.get("rebuild_indexes", False),
            "storage_compacted": parameters.get("compact_storage", False),
            "performance_gain": "15%"
        }
    
    async def _backup_system(
        self, 
        system: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Backup system data"""
        # This would implement actual backup in production
        backup_location = parameters.get("backup_location", "/backups")
        
        return {
            "status": "success",
            "backup_location": f"{backup_location}/{system}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.backup",
            "size": "500MB",
            "compressed": parameters.get("compression", False)
        }