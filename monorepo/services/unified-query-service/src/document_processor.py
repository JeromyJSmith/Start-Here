"""
Document Processor - Handles document parsing and processing pipelines
"""

import asyncio
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import structlog
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from .config import settings
from .models import DocumentFormat, DocumentStatus, MemorySource
from .adapters import (
    CogneeAdapter, MementoAdapter,
    MemOSAdapter, LlamaCloudAdapter
)

logger = structlog.get_logger()


class DocumentProcessor:
    """Processes documents through configurable pipelines"""
    
    def __init__(self):
        self.parser = None
        self.embedder = None
        self.tasks: Dict[str, DocumentStatus] = {}
        self.adapters: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize document processor components"""
        logger.info("Initializing Document Processor")
        
        # Initialize LlamaParse
        self.parser = LlamaParse(
            api_key=settings.LLAMA_INDEX_API_KEY,
            **settings.LLAMAPARSE_CONFIG
        )
        
        # Initialize embedder if available
        if settings.OPENAI_API_KEY:
            self.embedder = OpenAIEmbedding(
                api_key=settings.OPENAI_API_KEY
            )
        
        # Initialize storage adapters
        self.adapters = {
            "cognee": CogneeAdapter(settings.COGNEE_URL),
            "memento": MementoAdapter(settings.MEMENTO_URL),
            "memos": MemOSAdapter(settings.MEMOS_URL),
            "llamacloud": LlamaCloudAdapter(settings.LLAMACLOUD_URL)
        }
        
        # Initialize all adapters
        init_tasks = [adapter.initialize() for adapter in self.adapters.values()]
        await asyncio.gather(*init_tasks)
        
        self._initialized = True
        logger.info("Document Processor initialized")
    
    async def shutdown(self):
        """Shutdown document processor"""
        logger.info("Shutting down Document Processor")
        
        # Shutdown adapters
        shutdown_tasks = [adapter.shutdown() for adapter in self.adapters.values()]
        await asyncio.gather(*shutdown_tasks)
        
        self._initialized = False
    
    async def start_processing(
        self,
        file_path: str,
        pipeline: str = "default",
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        store_in: List[MemorySource] = None
    ) -> str:
        """Start document processing task"""
        task_id = str(uuid.uuid4())
        
        # Create task status
        self.tasks[task_id] = DocumentStatus(
            task_id=task_id,
            status="queued",
            progress=0.0,
            started_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Start processing in background
        asyncio.create_task(
            self._process_document(
                task_id, file_path, pipeline, output_format, store_in
            )
        )
        
        return task_id
    
    async def _process_document(
        self,
        task_id: str,
        file_path: str,
        pipeline: str,
        output_format: DocumentFormat,
        store_in: Optional[List[MemorySource]]
    ):
        """Process document through pipeline"""
        try:
            # Update status
            self._update_task_status(task_id, "processing", 0.0, "Starting pipeline")
            
            # Get pipeline steps
            steps = settings.DOCUMENT_PIPELINES.get(pipeline, ["parse"])
            total_steps = len(steps)
            
            # Execute pipeline
            result = {"file_path": file_path}
            
            for i, step in enumerate(steps):
                self._update_task_status(
                    task_id, "processing", 
                    (i / total_steps) * 100,
                    f"Executing step: {step}"
                )
                
                if step == "parse":
                    result = await self._step_parse(result)
                elif step == "chunk":
                    result = await self._step_chunk(result)
                elif step == "embed":
                    result = await self._step_embed(result)
                elif step == "enrich":
                    result = await self._step_enrich(result)
                elif step == "store":
                    result = await self._step_store(result, store_in)
                elif step == "citations":
                    result = await self._step_extract_citations(result)
                elif step == "syntax_highlight":
                    result = await self._step_syntax_highlight(result)
                elif step == "dependency_analysis":
                    result = await self._step_dependency_analysis(result)
                elif step == "clause_extraction":
                    result = await self._step_extract_clauses(result)
                elif step == "compliance_check":
                    result = await self._step_compliance_check(result)
                
                # Update completed steps
                self.tasks[task_id].steps_completed.append(step)
            
            # Format output
            formatted_result = self._format_output(result, output_format)
            
            # Complete task
            self._update_task_status(
                task_id, "completed", 100.0, "Processing complete",
                result=formatted_result
            )
            
        except Exception as e:
            logger.error("Document processing failed", 
                        task_id=task_id, error=str(e))
            self._update_task_status(
                task_id, "failed", 
                self.tasks[task_id].progress,
                f"Error: {str(e)}"
            )
            self.tasks[task_id].errors.append(str(e))
    
    async def _step_parse(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse document using LlamaParse"""
        file_path = context["file_path"]
        
        logger.info("Parsing document", file_path=file_path)
        start_time = time.time()
        
        # Parse document
        documents = await self.parser.aload_data(file_path)
        
        # Extract content
        content = "\n\n".join([doc.text for doc in documents])
        metadata = {}
        
        if documents:
            # Merge metadata from all documents
            for doc in documents:
                metadata.update(doc.metadata or {})
        
        context.update({
            "content": content,
            "documents": documents,
            "metadata": metadata,
            "parsing_time": time.time() - start_time
        })
        
        return context
    
    async def _step_chunk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Chunk document into smaller pieces"""
        content = context.get("content", "")
        
        # Use sentence splitter
        splitter = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=128,
            separator=" ",
        )
        
        # Split content
        chunks = splitter.split_text(content)
        
        context["chunks"] = chunks
        context["chunk_count"] = len(chunks)
        
        logger.info("Document chunked", chunks=len(chunks))
        
        return context
    
    async def _step_embed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings for chunks"""
        if not self.embedder:
            logger.warning("Embedder not available, skipping embedding step")
            return context
        
        chunks = context.get("chunks", [context.get("content", "")])
        
        # Generate embeddings
        embeddings = await self.embedder.aget_text_embedding_batch(chunks)
        
        context["embeddings"] = embeddings
        logger.info("Generated embeddings", count=len(embeddings))
        
        return context
    
    async def _step_enrich(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich document with additional metadata"""
        content = context.get("content", "")
        metadata = context.get("metadata", {})
        
        # Extract entities (simplified)
        entities = self._extract_entities(content)
        
        # Extract keywords
        keywords = self._extract_keywords(content)
        
        # Add enrichment data
        metadata.update({
            "entities": entities,
            "keywords": keywords,
            "word_count": len(content.split()),
            "enriched_at": datetime.utcnow().isoformat()
        })
        
        context["metadata"] = metadata
        logger.info("Document enriched", entities=len(entities), keywords=len(keywords))
        
        return context
    
    async def _step_store(
        self, 
        context: Dict[str, Any], 
        store_in: Optional[List[MemorySource]]
    ) -> Dict[str, Any]:
        """Store document in specified memory systems"""
        if not store_in:
            store_in = list(MemorySource)
        
        chunks = context.get("chunks", [context.get("content", "")])
        embeddings = context.get("embeddings", [])
        metadata = context.get("metadata", {})
        
        storage_results = {}
        
        for source in store_in:
            if source not in self.adapters:
                continue
            
            try:
                adapter = self.adapters[source]
                
                # Store each chunk
                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    chunk_metadata = {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                    
                    # Add embedding if available
                    if i < len(embeddings):
                        chunk_metadata["embedding"] = embeddings[i]
                    
                    chunk_id = await adapter.store(chunk, chunk_metadata)
                    chunk_ids.append(chunk_id)
                
                storage_results[source] = {
                    "status": "success",
                    "chunks_stored": len(chunk_ids),
                    "ids": chunk_ids
                }
                
            except Exception as e:
                logger.error(f"Failed to store in {source}", error=str(e))
                storage_results[source] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        context["storage_results"] = storage_results
        logger.info("Document stored", results=storage_results)
        
        return context
    
    async def _step_extract_citations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract citations from document"""
        content = context.get("content", "")
        
        # Simple citation extraction (would use more sophisticated NLP in production)
        citations = []
        
        # Look for common citation patterns
        import re
        
        # Pattern for (Author, Year) style
        pattern1 = r'\(([A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+)*),\s*(\d{4})\)'
        citations.extend(re.findall(pattern1, content))
        
        # Pattern for [Number] style
        pattern2 = r'\[(\d+)\]'
        ref_numbers = re.findall(pattern2, content)
        
        context["citations"] = {
            "author_year": citations,
            "numbered": ref_numbers,
            "total_count": len(citations) + len(ref_numbers)
        }
        
        return context
    
    async def _step_syntax_highlight(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply syntax highlighting to code blocks"""
        content = context.get("content", "")
        
        # This would use a proper syntax highlighter in production
        # For now, just identify code blocks
        import re
        
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        context["code_blocks"] = [
            {"language": lang or "unknown", "code": code}
            for lang, code in code_blocks
        ]
        
        return context
    
    async def _step_dependency_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code dependencies"""
        code_blocks = context.get("code_blocks", [])
        
        dependencies = {
            "imports": [],
            "packages": [],
            "functions": []
        }
        
        for block in code_blocks:
            code = block.get("code", "")
            
            # Extract imports (simplified)
            import re
            
            # Python imports
            py_imports = re.findall(r'^import\s+(\S+)', code, re.MULTILINE)
            py_from_imports = re.findall(r'^from\s+(\S+)\s+import', code, re.MULTILINE)
            
            dependencies["imports"].extend(py_imports + py_from_imports)
        
        # Deduplicate
        dependencies["imports"] = list(set(dependencies["imports"]))
        
        context["dependencies"] = dependencies
        
        return context
    
    async def _step_extract_clauses(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract legal clauses from document"""
        content = context.get("content", "")
        
        # This would use NLP for clause extraction in production
        # For now, look for numbered sections
        import re
        
        clauses = []
        
        # Pattern for numbered sections
        section_pattern = r'^(\d+(?:\.\d+)*)\s+([^\n]+)'
        matches = re.findall(section_pattern, content, re.MULTILINE)
        
        for number, title in matches:
            clauses.append({
                "number": number,
                "title": title.strip(),
                "type": self._classify_clause(title)
            })
        
        context["clauses"] = clauses
        
        return context
    
    async def _step_compliance_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check document for compliance issues"""
        content = context.get("content", "")
        clauses = context.get("clauses", [])
        
        # Simple compliance checks
        compliance_issues = []
        
        # Check for required clauses (example)
        required_clauses = ["privacy", "data protection", "liability"]
        
        clause_titles = [c.get("title", "").lower() for c in clauses]
        
        for required in required_clauses:
            if not any(required in title for title in clause_titles):
                compliance_issues.append({
                    "type": "missing_clause",
                    "severity": "medium",
                    "description": f"Missing required clause: {required}"
                })
        
        context["compliance"] = {
            "issues": compliance_issues,
            "compliant": len(compliance_issues) == 0
        }
        
        return context
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities from content"""
        # This would use NER in production
        # For now, extract capitalized words
        import re
        
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Filter common words
        common_words = {"The", "This", "That", "These", "Those", "A", "An"}
        entities = [w for w in words if w not in common_words]
        
        # Deduplicate and limit
        return list(set(entities))[:50]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # This would use TF-IDF or similar in production
        # For now, extract frequently occurring words
        import re
        from collections import Counter
        
        # Extract words
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter short and common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = [w for w in words if len(w) > 3 and w not in stopwords]
        
        # Get most common
        word_counts = Counter(words)
        keywords = [word for word, _ in word_counts.most_common(20)]
        
        return keywords
    
    def _classify_clause(self, title: str) -> str:
        """Classify clause type based on title"""
        title_lower = title.lower()
        
        if any(term in title_lower for term in ["privacy", "data protection", "gdpr"]):
            return "privacy"
        elif any(term in title_lower for term in ["liability", "limitation", "disclaimer"]):
            return "liability"
        elif any(term in title_lower for term in ["payment", "fee", "pricing"]):
            return "financial"
        elif any(term in title_lower for term in ["termination", "cancellation"]):
            return "termination"
        else:
            return "general"
    
    def _format_output(
        self, 
        result: Dict[str, Any], 
        output_format: DocumentFormat
    ) -> Dict[str, Any]:
        """Format processing result based on requested format"""
        if output_format == DocumentFormat.JSON:
            return result
        
        elif output_format == DocumentFormat.MARKDOWN:
            # Convert to markdown format
            content = f"# Document Processing Result\n\n"
            content += f"**File**: {result.get('file_path', 'Unknown')}\n\n"
            
            if "metadata" in result:
                content += "## Metadata\n"
                for key, value in result["metadata"].items():
                    if key not in ["embeddings"]:  # Skip embeddings
                        content += f"- **{key}**: {value}\n"
                content += "\n"
            
            content += "## Content\n\n"
            content += result.get("content", "")
            
            return {"formatted_content": content, "metadata": result.get("metadata", {})}
        
        else:  # STRUCTURED
            # Return structured format
            return {
                "document": {
                    "file_path": result.get("file_path"),
                    "content": result.get("content"),
                    "chunks": result.get("chunks", []),
                    "metadata": result.get("metadata", {})
                },
                "analysis": {
                    "citations": result.get("citations", {}),
                    "entities": result.get("metadata", {}).get("entities", []),
                    "keywords": result.get("metadata", {}).get("keywords", []),
                    "code_blocks": result.get("code_blocks", []),
                    "dependencies": result.get("dependencies", {}),
                    "clauses": result.get("clauses", []),
                    "compliance": result.get("compliance", {})
                },
                "storage": result.get("storage_results", {})
            }
    
    def _update_task_status(
        self,
        task_id: str,
        status: str,
        progress: float,
        current_step: str,
        result: Optional[Dict[str, Any]] = None
    ):
        """Update task status"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = status
        task.progress = progress
        task.current_step = current_step
        task.updated_at = datetime.utcnow()
        
        if result:
            task.result = result
        
        if status == "completed":
            task.completed_at = datetime.utcnow()
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        if task_id not in self.tasks:
            return None
        
        return self.tasks[task_id].dict()
    
    async def track_processing(self, task_id: str):
        """Track document processing progress"""
        # This would implement real-time progress tracking
        # For now, just log progress
        while task_id in self.tasks and self.tasks[task_id].status == "processing":
            task = self.tasks[task_id]
            logger.info("Processing progress", 
                       task_id=task_id,
                       progress=task.progress,
                       step=task.current_step)
            await asyncio.sleep(5)
    
    async def parse_document(self, file_path: str) -> Dict[str, Any]:
        """Parse a single document"""
        context = {"file_path": file_path}
        result = await self._step_parse(context)
        
        return {
            "content": result.get("content"),
            "metadata": result.get("metadata"),
            "parsing_time": result.get("parsing_time")
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get document processing statistics"""
        completed_tasks = [t for t in self.tasks.values() if t.status == "completed"]
        failed_tasks = [t for t in self.tasks.values() if t.status == "failed"]
        
        # Calculate average processing time
        processing_times = []
        for task in completed_tasks:
            if task.completed_at and task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                processing_times.append(duration)
        
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "total_processed": len(completed_tasks),
            "total_failed": len(failed_tasks),
            "average_processing_time": avg_time,
            "success_rate": len(completed_tasks) / len(self.tasks) if self.tasks else 0,
            "active_tasks": len([t for t in self.tasks.values() if t.status == "processing"])
        }