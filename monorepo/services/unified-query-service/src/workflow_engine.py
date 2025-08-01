"""
Workflow Engine - Manages workflow deployment and execution using llama_deploy
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import structlog
from llama_deploy import (
    deploy_workflow,
    WorkflowService,
    ControlPlaneServer,
    SimpleMessageQueue
)
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step
)

from .config import settings
from .models import WorkflowTrigger, WorkflowStatus
from .workflows import (
    MemorySyncWorkflow,
    DocumentIngestionWorkflow,
    QueryEnhancementWorkflow,
    MaintenanceWorkflow
)

logger = structlog.get_logger()


class WorkflowEngine:
    """Manages workflow deployment and execution"""
    
    def __init__(self):
        self.control_plane = None
        self.message_queue = None
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, Workflow] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize workflow engine components"""
        logger.info("Initializing Workflow Engine")
        
        # Initialize message queue
        self.message_queue = SimpleMessageQueue()
        
        # Initialize control plane
        self.control_plane = ControlPlaneServer(
            message_queue=self.message_queue,
            host="0.0.0.0",
            port=settings.LLAMA_DEPLOY_CONFIG["control_plane_port"]
        )
        
        # Start control plane
        await self.control_plane.launch_server()
        
        # Register built-in workflows
        await self._register_builtin_workflows()
        
        self._initialized = True
        logger.info("Workflow Engine initialized",
                   workflows=list(self.workflows.keys()))
    
    async def _register_builtin_workflows(self):
        """Register built-in workflows"""
        if "memory_sync" in settings.ENABLED_WORKFLOWS:
            self.workflows["memory_sync"] = MemorySyncWorkflow()
        
        if "document_ingestion" in settings.ENABLED_WORKFLOWS:
            self.workflows["document_ingestion"] = DocumentIngestionWorkflow()
        
        if "query_enhancement" in settings.ENABLED_WORKFLOWS:
            self.workflows["query_enhancement"] = QueryEnhancementWorkflow()
        
        if "maintenance" in settings.ENABLED_WORKFLOWS:
            self.workflows["maintenance"] = MaintenanceWorkflow()
    
    async def shutdown(self):
        """Shutdown workflow engine"""
        logger.info("Shutting down Workflow Engine")
        
        # Stop all deployments
        for deployment_id in list(self.deployments.keys()):
            await self._stop_deployment(deployment_id)
        
        # Stop control plane
        if self.control_plane:
            await self.control_plane.shutdown()
        
        self._initialized = False
    
    async def deploy_workflow(
        self,
        workflow_id: str,
        config: Dict[str, Any],
        triggers: List[WorkflowTrigger]
    ) -> Dict[str, Any]:
        """Deploy a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_id}")
        
        deployment_id = str(uuid.uuid4())
        logger.info("Deploying workflow", 
                   workflow_id=workflow_id,
                   deployment_id=deployment_id)
        
        # Get workflow instance
        workflow = self.workflows[workflow_id]
        
        # Configure workflow
        workflow = self._configure_workflow(workflow, config)
        
        # Allocate port for service
        port = self._allocate_port()
        
        # Create workflow service
        service = WorkflowService(
            workflow=workflow,
            message_queue=self.message_queue,
            service_name=f"{workflow_id}_{deployment_id}",
            host="0.0.0.0",
            port=port
        )
        
        # Deploy the service
        await deploy_workflow(
            workflow=workflow,
            workflow_config=config,
            host="0.0.0.0",
            port=port,
            service_name=f"{workflow_id}_{deployment_id}"
        )
        
        # Set up triggers
        await self._setup_triggers(deployment_id, triggers, service)
        
        # Store deployment info
        self.deployments[deployment_id] = {
            "workflow_id": workflow_id,
            "deployment_id": deployment_id,
            "service": service,
            "port": port,
            "triggers": triggers,
            "status": "deployed",
            "created_at": datetime.utcnow(),
            "config": config,
            "executions": 0,
            "last_execution": None,
            "endpoints": [
                f"http://localhost:{port}/run",
                f"http://localhost:{port}/status"
            ]
        }
        
        return {
            "workflow_id": workflow_id,
            "deployment_id": deployment_id,
            "status": "deployed",
            "endpoints": self.deployments[deployment_id]["endpoints"]
        }
    
    async def execute_workflow(
        self,
        workflow_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a deployed workflow"""
        # Find deployment for workflow
        deployment = None
        for dep in self.deployments.values():
            if dep["workflow_id"] == workflow_id and dep["status"] == "deployed":
                deployment = dep
                break
        
        if not deployment:
            raise ValueError(f"No active deployment found for workflow: {workflow_id}")
        
        logger.info("Executing workflow",
                   workflow_id=workflow_id,
                   deployment_id=deployment["deployment_id"])
        
        execution_id = str(uuid.uuid4())
        
        try:
            # Get workflow service
            service = deployment["service"]
            
            # Create start event with payload
            start_event = StartEvent(**payload)
            
            # Execute workflow
            result = await service.run_workflow(start_event)
            
            # Update execution stats
            deployment["executions"] += 1
            deployment["last_execution"] = datetime.utcnow()
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result.result if hasattr(result, 'result') else str(result)
            }
            
        except Exception as e:
            logger.error("Workflow execution failed",
                        workflow_id=workflow_id,
                        error=str(e))
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def get_workflow_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow deployment status"""
        if deployment_id not in self.deployments:
            return None
        
        deployment = self.deployments[deployment_id]
        
        return WorkflowStatus(
            deployment_id=deployment_id,
            workflow_id=deployment["workflow_id"],
            status=deployment["status"],
            executions=deployment["executions"],
            last_execution=deployment["last_execution"],
            errors=[],  # Would track errors in production
            metrics={
                "port": deployment["port"],
                "triggers": len(deployment["triggers"]),
                "uptime": (datetime.utcnow() - deployment["created_at"]).total_seconds()
            }
        ).dict()
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflows"""
        workflows = []
        
        for workflow_id, workflow in self.workflows.items():
            # Get workflow metadata
            workflows.append({
                "id": workflow_id,
                "name": workflow.__class__.__name__,
                "description": workflow.__doc__ or "No description",
                "deployments": [
                    dep_id for dep_id, dep in self.deployments.items()
                    if dep["workflow_id"] == workflow_id
                ],
                "available": True
            })
        
        return workflows
    
    def _configure_workflow(
        self,
        workflow: Workflow,
        config: Dict[str, Any]
    ) -> Workflow:
        """Configure workflow with provided settings"""
        # Apply configuration to workflow
        # This would be workflow-specific in production
        for key, value in config.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        return workflow
    
    def _allocate_port(self) -> int:
        """Allocate a port for workflow service"""
        # Simple port allocation
        # In production, would track used ports
        start_port, end_port = settings.WORKFLOW_PORT_RANGE
        
        used_ports = {dep["port"] for dep in self.deployments.values()}
        
        for port in range(start_port, end_port + 1):
            if port not in used_ports:
                return port
        
        raise RuntimeError("No available ports for workflow deployment")
    
    async def _setup_triggers(
        self,
        deployment_id: str,
        triggers: List[WorkflowTrigger],
        service: WorkflowService
    ):
        """Set up workflow triggers"""
        for trigger in triggers:
            if trigger == WorkflowTrigger.SCHEDULE:
                # Set up scheduled execution
                await self._setup_schedule_trigger(deployment_id, service)
            elif trigger == WorkflowTrigger.EVENT:
                # Set up event-based trigger
                await self._setup_event_trigger(deployment_id, service)
            elif trigger == WorkflowTrigger.WEBHOOK:
                # Set up webhook trigger
                await self._setup_webhook_trigger(deployment_id, service)
            # MANUAL trigger requires no setup
    
    async def _setup_schedule_trigger(
        self,
        deployment_id: str,
        service: WorkflowService
    ):
        """Set up scheduled workflow execution"""
        # This would use a scheduler like APScheduler in production
        logger.info("Setting up schedule trigger", deployment_id=deployment_id)
        
        # Example: Run every hour
        async def scheduled_run():
            while deployment_id in self.deployments:
                await asyncio.sleep(3600)  # 1 hour
                if deployment_id in self.deployments:
                    await self.execute_workflow(
                        self.deployments[deployment_id]["workflow_id"],
                        {"trigger": "schedule"}
                    )
        
        asyncio.create_task(scheduled_run())
    
    async def _setup_event_trigger(
        self,
        deployment_id: str,
        service: WorkflowService
    ):
        """Set up event-based workflow trigger"""
        logger.info("Setting up event trigger", deployment_id=deployment_id)
        
        # This would subscribe to an event bus in production
        # For now, we'll use the message queue
        async def event_listener():
            while deployment_id in self.deployments:
                # Listen for events on the message queue
                event = await self.message_queue.get(
                    f"events_{deployment_id}",
                    timeout=10.0
                )
                if event:
                    await self.execute_workflow(
                        self.deployments[deployment_id]["workflow_id"],
                        {"trigger": "event", "event_data": event}
                    )
        
        asyncio.create_task(event_listener())
    
    async def _setup_webhook_trigger(
        self,
        deployment_id: str,
        service: WorkflowService
    ):
        """Set up webhook trigger for workflow"""
        logger.info("Setting up webhook trigger", deployment_id=deployment_id)
        
        # This would register a webhook endpoint in production
        # The endpoint would be added to the service's endpoints
        deployment = self.deployments[deployment_id]
        deployment["endpoints"].append(
            f"http://localhost:{deployment['port']}/webhook"
        )
    
    async def _stop_deployment(self, deployment_id: str):
        """Stop a workflow deployment"""
        if deployment_id not in self.deployments:
            return
        
        deployment = self.deployments[deployment_id]
        logger.info("Stopping deployment", deployment_id=deployment_id)
        
        # Stop the service
        service = deployment["service"]
        if hasattr(service, 'shutdown'):
            await service.shutdown()
        
        # Update status
        deployment["status"] = "stopped"
        
        # Remove from deployments
        del self.deployments[deployment_id]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get workflow engine statistics"""
        total_executions = sum(dep["executions"] for dep in self.deployments.values())
        
        executions_by_workflow = {}
        for dep in self.deployments.values():
            workflow_id = dep["workflow_id"]
            executions_by_workflow[workflow_id] = \
                executions_by_workflow.get(workflow_id, 0) + dep["executions"]
        
        return {
            "total_deployments": len(self.deployments),
            "active_deployments": len([d for d in self.deployments.values() 
                                     if d["status"] == "deployed"]),
            "total_executions": total_executions,
            "executions_by_workflow": executions_by_workflow,
            "available_workflows": len(self.workflows)
        }