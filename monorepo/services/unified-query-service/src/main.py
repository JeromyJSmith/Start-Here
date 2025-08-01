"""
Unified Query Service - Main Application
Orchestrates queries across multiple memory systems
"""

import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog

from .config import settings
from .orchestrator import QueryOrchestrator
from .document_processor import DocumentProcessor
from .workflow_engine import WorkflowEngine
from .models import (
    QueryRequest, QueryResponse, QueryMode,
    DocumentProcessRequest, DocumentProcessResponse,
    WorkflowDeployRequest, WorkflowDeployResponse
)

# Configure structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Unified Query Service", 
                port=settings.SERVICE_PORT,
                memory_systems=settings.ENABLED_MEMORY_SYSTEMS)
    
    # Initialize components
    app.state.orchestrator = QueryOrchestrator()
    app.state.document_processor = DocumentProcessor()
    app.state.workflow_engine = WorkflowEngine()
    
    # Start background tasks
    await app.state.orchestrator.initialize()
    await app.state.document_processor.initialize()
    await app.state.workflow_engine.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Unified Query Service")
    await app.state.orchestrator.shutdown()
    await app.state.document_processor.shutdown()
    await app.state.workflow_engine.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Unified Query Service",
    description="Orchestrates queries across Cognee, Memento, MemOS, and LlamaCloud",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check health of service and all connected systems"""
    orchestrator: QueryOrchestrator = app.state.orchestrator
    
    health_status = await orchestrator.check_health()
    
    # Overall health is healthy if at least one system is up
    overall_healthy = any(system["status"] == "healthy" 
                          for system in health_status["systems"])
    
    if not overall_healthy:
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


# Query endpoints
@app.post("/api/query", response_model=QueryResponse)
async def unified_query(request: QueryRequest):
    """
    Execute a query across multiple memory systems
    
    Modes:
    - unified: Query all systems and merge results
    - sequential: Query systems in order, using context
    - parallel: Query all systems, return grouped results
    - smart: Intelligently route based on query analysis
    """
    orchestrator: QueryOrchestrator = app.state.orchestrator
    
    try:
        result = await orchestrator.query(
            query=request.query,
            mode=request.mode,
            sources=request.sources,
            options=request.options.dict() if request.options else {}
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error("Query failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/analyze")
async def analyze_query(query: str):
    """Analyze a query to determine optimal routing"""
    orchestrator: QueryOrchestrator = app.state.orchestrator
    
    analysis = await orchestrator.analyze_query(query)
    return {
        "query": query,
        "analysis": analysis,
        "recommended_mode": analysis.get("mode", "smart"),
        "recommended_sources": analysis.get("sources", [])
    }


# Document processing endpoints
@app.post("/api/document/process", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Process a document through the configured pipeline
    
    Pipelines:
    - default: Parse, chunk, embed, enrich, store
    - custom: User-defined pipeline steps
    """
    processor: DocumentProcessor = app.state.document_processor
    
    # Start processing in background
    task_id = await processor.start_processing(
        file_path=request.file_path,
        pipeline=request.pipeline,
        output_format=request.output_format,
        store_in=request.store_in
    )
    
    # Add background task to track progress
    background_tasks.add_task(
        processor.track_processing,
        task_id
    )
    
    return DocumentProcessResponse(
        task_id=task_id,
        status="processing",
        message=f"Document processing started with {request.pipeline} pipeline"
    )


@app.get("/api/document/status/{task_id}")
async def document_status(task_id: str):
    """Check status of document processing task"""
    processor: DocumentProcessor = app.state.document_processor
    
    status = await processor.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status


@app.post("/api/document/parse")
async def parse_document(file_path: str):
    """Parse a document using LlamaParse"""
    processor: DocumentProcessor = app.state.document_processor
    
    try:
        result = await processor.parse_document(file_path)
        return {
            "file_path": file_path,
            "content": result.get("content"),
            "metadata": result.get("metadata"),
            "parsing_time": result.get("parsing_time")
        }
    except Exception as e:
        logger.error("Document parsing failed", error=str(e), file=file_path)
        raise HTTPException(status_code=500, detail=str(e))


# Workflow endpoints
@app.post("/api/workflow/deploy", response_model=WorkflowDeployResponse)
async def deploy_workflow(request: WorkflowDeployRequest):
    """Deploy a workflow using llama_deploy"""
    engine: WorkflowEngine = app.state.workflow_engine
    
    try:
        deployment = await engine.deploy_workflow(
            workflow_id=request.workflow_id,
            config=request.config,
            triggers=request.triggers
        )
        
        return WorkflowDeployResponse(
            workflow_id=deployment["workflow_id"],
            deployment_id=deployment["deployment_id"],
            status=deployment["status"],
            endpoints=deployment.get("endpoints", [])
        )
    except Exception as e:
        logger.error("Workflow deployment failed", 
                    error=str(e), 
                    workflow_id=request.workflow_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/list")
async def list_workflows():
    """List all available workflows"""
    engine: WorkflowEngine = app.state.workflow_engine
    
    workflows = await engine.list_workflows()
    return {"workflows": workflows}


@app.get("/api/workflow/status/{deployment_id}")
async def workflow_status(deployment_id: str):
    """Check status of deployed workflow"""
    engine: WorkflowEngine = app.state.workflow_engine
    
    status = await engine.get_workflow_status(deployment_id)
    if not status:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return status


@app.post("/api/workflow/execute/{workflow_id}")
async def execute_workflow(workflow_id: str, payload: Dict[str, Any]):
    """Execute a deployed workflow"""
    engine: WorkflowEngine = app.state.workflow_engine
    
    try:
        result = await engine.execute_workflow(workflow_id, payload)
        return {
            "workflow_id": workflow_id,
            "execution_id": result.get("execution_id"),
            "status": result.get("status"),
            "result": result.get("result")
        }
    except Exception as e:
        logger.error("Workflow execution failed",
                    error=str(e),
                    workflow_id=workflow_id)
        raise HTTPException(status_code=500, detail=str(e))


# Statistics and monitoring endpoints
@app.get("/api/stats")
async def get_statistics():
    """Get service statistics and metrics"""
    orchestrator: QueryOrchestrator = app.state.orchestrator
    processor: DocumentProcessor = app.state.document_processor
    engine: WorkflowEngine = app.state.workflow_engine
    
    stats = {
        "query_stats": await orchestrator.get_stats(),
        "document_stats": await processor.get_stats(),
        "workflow_stats": await engine.get_stats()
    }
    
    return stats


@app.get("/api/config")
async def get_configuration():
    """Get current service configuration"""
    return {
        "memory_systems": settings.MEMORY_SYSTEM_CONFIG,
        "document_processing": {
            "pipelines": settings.DOCUMENT_PIPELINES,
            "supported_formats": settings.SUPPORTED_FORMATS
        },
        "workflows": {
            "available": await app.state.workflow_engine.list_workflows(),
            "port_range": settings.WORKFLOW_PORT_RANGE
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )