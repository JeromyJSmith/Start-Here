"""
Data models for Unified Query Service
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Enums
class QueryMode(str, Enum):
    """Query execution modes"""
    UNIFIED = "unified"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    SMART = "smart"


class MemorySource(str, Enum):
    """Available memory sources"""
    COGNEE = "cognee"
    MEMENTO = "memento"
    MEMOS = "memos"
    LLAMACLOUD = "llamacloud"


class DocumentFormat(str, Enum):
    """Supported document output formats"""
    MARKDOWN = "markdown"
    JSON = "json"
    STRUCTURED = "structured"


class RankingStrategy(str, Enum):
    """Result ranking strategies"""
    RELEVANCE = "relevance"
    RECENCY = "recency"
    HYBRID = "hybrid"


# Query models
class QueryOptions(BaseModel):
    """Options for query execution"""
    max_results: int = Field(10, ge=1, le=100)
    include_metadata: bool = True
    ranking_strategy: RankingStrategy = RankingStrategy.HYBRID
    filters: Optional[Dict[str, Any]] = None
    boost_recent: bool = False
    deduplicate: bool = True


class QueryRequest(BaseModel):
    """Query request model"""
    query: str = Field(..., min_length=1, max_length=1000)
    mode: QueryMode = QueryMode.SMART
    sources: Optional[List[MemorySource]] = None
    options: Optional[QueryOptions] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    """Individual query result"""
    id: str
    content: str
    source: MemorySource
    score: float = Field(..., ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    highlights: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    mode: QueryMode
    results: List[QueryResult]
    total_results: int
    processing_time: float
    sources_queried: List[MemorySource]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Document processing models
class DocumentProcessRequest(BaseModel):
    """Document processing request"""
    file_path: str
    pipeline: str = "default"
    output_format: DocumentFormat = DocumentFormat.MARKDOWN
    store_in: List[MemorySource] = Field(default_factory=lambda: list(MemorySource))
    metadata: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None


class DocumentProcessResponse(BaseModel):
    """Document processing response"""
    task_id: str
    status: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentStatus(BaseModel):
    """Document processing status"""
    task_id: str
    status: str
    progress: float = Field(0.0, ge=0, le=100)
    current_step: Optional[str] = None
    steps_completed: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


# Workflow models
class WorkflowTrigger(str, Enum):
    """Workflow trigger types"""
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    WEBHOOK = "webhook"


class WorkflowDeployRequest(BaseModel):
    """Workflow deployment request"""
    workflow_id: str
    config: Dict[str, Any] = Field(default_factory=dict)
    triggers: List[WorkflowTrigger] = Field(default_factory=lambda: [WorkflowTrigger.MANUAL])
    environment: Optional[Dict[str, str]] = None
    resources: Optional[Dict[str, Any]] = None


class WorkflowDeployResponse(BaseModel):
    """Workflow deployment response"""
    workflow_id: str
    deployment_id: str
    status: str
    endpoints: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStatus(BaseModel):
    """Workflow execution status"""
    deployment_id: str
    workflow_id: str
    status: str
    executions: int = 0
    last_execution: Optional[datetime] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


# Health check models
class SystemHealth(BaseModel):
    """Individual system health status"""
    name: str
    status: str
    latency: Optional[float] = None
    last_check: datetime
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Service health response"""
    service: str
    status: str
    version: str
    uptime: float
    systems: List[SystemHealth]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Statistics models
class QueryStats(BaseModel):
    """Query statistics"""
    total_queries: int = 0
    queries_by_mode: Dict[str, int] = Field(default_factory=dict)
    queries_by_source: Dict[str, int] = Field(default_factory=dict)
    average_latency: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0


class DocumentStats(BaseModel):
    """Document processing statistics"""
    total_processed: int = 0
    documents_by_format: Dict[str, int] = Field(default_factory=dict)
    documents_by_pipeline: Dict[str, int] = Field(default_factory=dict)
    average_processing_time: float = 0.0
    success_rate: float = 0.0


class WorkflowStats(BaseModel):
    """Workflow execution statistics"""
    total_deployments: int = 0
    total_executions: int = 0
    executions_by_workflow: Dict[str, int] = Field(default_factory=dict)
    average_execution_time: float = 0.0
    success_rate: float = 0.0


class ServiceStats(BaseModel):
    """Overall service statistics"""
    query_stats: QueryStats
    document_stats: DocumentStats
    workflow_stats: WorkflowStats
    timestamp: datetime = Field(default_factory=datetime.utcnow)