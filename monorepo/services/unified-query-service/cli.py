#!/usr/bin/env python3
"""
CLI for Unified Query Service
"""

import asyncio
import json
import sys
from typing import Optional, List
from pathlib import Path

import click
import httpx
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Default service URL
DEFAULT_URL = "http://localhost:8505"


@click.group()
@click.option("--url", default=DEFAULT_URL, help="Unified Query Service URL")
@click.pass_context
def cli(ctx, url):
    """Unified Query Service CLI"""
    ctx.ensure_object(dict)
    ctx.obj["url"] = url


@cli.command()
@click.argument("query")
@click.option("--mode", type=click.Choice(["unified", "sequential", "parallel", "smart"]), 
              default="smart", help="Query mode")
@click.option("--sources", multiple=True, 
              help="Memory sources to query (cognee, memento, memos, llamacloud)")
@click.option("--max-results", type=int, default=10, help="Maximum results")
@click.option("--format", type=click.Choice(["json", "table", "markdown"]), 
              default="table", help="Output format")
@click.pass_context
def query(ctx, query, mode, sources, max_results, format):
    """Execute a query across memory systems"""
    url = ctx.obj["url"]
    
    async def run_query():
        async with httpx.AsyncClient() as client:
            payload = {
                "query": query,
                "mode": mode,
                "options": {
                    "max_results": max_results
                }
            }
            
            if sources:
                payload["sources"] = list(sources)
            
            response = await client.post(f"{url}/api/query", json=payload)
            response.raise_for_status()
            
            return response.json()
    
    with console.status(f"Querying: {query}..."):
        result = asyncio.run(run_query())
    
    # Display results
    if format == "json":
        print(json.dumps(result, indent=2))
    
    elif format == "table":
        table = Table(title=f"Query Results for: {query}")
        table.add_column("Source", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Content", style="white", overflow="fold")
        
        for res in result["results"]:
            table.add_row(
                res["source"],
                f"{res['score']:.3f}",
                res["content"][:100] + "..." if len(res["content"]) > 100 else res["content"]
            )
        
        console.print(table)
        console.print(f"\nTotal results: {result['total_results']}")
        console.print(f"Processing time: {result['processing_time']:.2f}s")
    
    else:  # markdown
        console.print(f"# Query Results\n")
        console.print(f"**Query**: {query}")
        console.print(f"**Mode**: {mode}")
        console.print(f"**Total Results**: {result['total_results']}\n")
        
        for i, res in enumerate(result["results"], 1):
            console.print(f"## Result {i}")
            console.print(f"- **Source**: {res['source']}")
            console.print(f"- **Score**: {res['score']:.3f}")
            console.print(f"- **Content**: {res['content']}\n")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--pipeline", default="default", 
              help="Processing pipeline (default, fast, research, code, legal)")
@click.option("--format", type=click.Choice(["markdown", "json", "structured"]), 
              default="markdown", help="Output format")
@click.option("--store-in", multiple=True,
              help="Memory systems to store in (cognee, memento, memos, llamacloud)")
@click.pass_context
def process(ctx, file_path, pipeline, format, store_in):
    """Process a document"""
    url = ctx.obj["url"]
    
    async def process_document():
        async with httpx.AsyncClient() as client:
            payload = {
                "file_path": str(Path(file_path).absolute()),
                "pipeline": pipeline,
                "output_format": format
            }
            
            if store_in:
                payload["store_in"] = list(store_in)
            
            response = await client.post(f"{url}/api/document/process", json=payload)
            response.raise_for_status()
            
            return response.json()
    
    with console.status(f"Processing document: {file_path}..."):
        result = asyncio.run(process_document())
    
    console.print(Panel(f"Task ID: {result['task_id']}", title="Document Processing Started"))
    console.print(f"Status: {result['status']}")
    console.print(f"Message: {result['message']}")
    
    # Option to track progress
    if click.confirm("Track processing progress?"):
        track_task(ctx, result['task_id'])


@cli.command()
@click.argument("task_id")
@click.pass_context
def track_task(ctx, task_id):
    """Track document processing task"""
    url = ctx.obj["url"]
    
    async def get_status():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/api/document/status/{task_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    
    with console.status(f"Tracking task: {task_id}...") as status:
        while True:
            task_status = asyncio.run(get_status())
            
            if not task_status:
                console.print("[red]Task not found[/red]")
                break
            
            # Update status
            status.update(
                f"Task {task_id}: {task_status['status']} "
                f"({task_status['progress']:.0f}%)"
            )
            
            if task_status['status'] in ['completed', 'failed']:
                break
            
            asyncio.run(asyncio.sleep(2))
    
    # Display final status
    if task_status:
        console.print(Panel(
            f"Status: {task_status['status']}\n"
            f"Progress: {task_status['progress']:.0f}%\n"
            f"Steps: {', '.join(task_status['steps_completed'])}",
            title=f"Task {task_id}"
        ))
        
        if task_status['status'] == 'failed' and task_status['errors']:
            console.print("[red]Errors:[/red]")
            for error in task_status['errors']:
                console.print(f"  - {error}")


@cli.command()
@click.argument("workflow_id")
@click.option("--config", type=str, help="JSON configuration for workflow")
@click.option("--triggers", multiple=True, 
              type=click.Choice(["event", "schedule", "manual", "webhook"]),
              default=["manual"], help="Workflow triggers")
@click.pass_context
def deploy(ctx, workflow_id, config, triggers):
    """Deploy a workflow"""
    url = ctx.obj["url"]
    
    async def deploy_workflow():
        async with httpx.AsyncClient() as client:
            payload = {
                "workflow_id": workflow_id,
                "config": json.loads(config) if config else {},
                "triggers": list(triggers)
            }
            
            response = await client.post(f"{url}/api/workflow/deploy", json=payload)
            response.raise_for_status()
            
            return response.json()
    
    with console.status(f"Deploying workflow: {workflow_id}..."):
        result = asyncio.run(deploy_workflow())
    
    console.print(Panel(
        f"Workflow ID: {result['workflow_id']}\n"
        f"Deployment ID: {result['deployment_id']}\n"
        f"Status: {result['status']}\n"
        f"Endpoints:\n" + "\n".join(f"  - {ep}" for ep in result['endpoints']),
        title="Workflow Deployed"
    ))


@cli.command()
@click.pass_context
def workflows(ctx):
    """List available workflows"""
    url = ctx.obj["url"]
    
    async def list_workflows():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/api/workflow/list")
            response.raise_for_status()
            return response.json()
    
    result = asyncio.run(list_workflows())
    
    table = Table(title="Available Workflows")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Deployments", style="yellow")
    
    for workflow in result["workflows"]:
        table.add_row(
            workflow["id"],
            workflow["name"],
            workflow["description"][:50] + "..." if len(workflow["description"]) > 50 else workflow["description"],
            str(len(workflow["deployments"]))
        )
    
    console.print(table)


@cli.command()
@click.pass_context
def health(ctx):
    """Check service health"""
    url = ctx.obj["url"]
    
    async def check_health():
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{url}/health")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    result = asyncio.run(check_health())
    
    if "error" in result:
        console.print(f"[red]Service unavailable: {result['error']}[/red]")
        return
    
    # Display health status
    table = Table(title="Service Health")
    table.add_column("System", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Latency", style="yellow")
    
    for system in result.get("systems", []):
        status_color = "green" if system["status"] == "healthy" else "red"
        table.add_row(
            system["name"],
            f"[{status_color}]{system['status']}[/{status_color}]",
            f"{system.get('latency', 0)*1000:.0f}ms" if system.get('latency') else "N/A"
        )
    
    console.print(table)
    console.print(f"\nOverall Status: {result.get('status', 'unknown')}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show service statistics"""
    url = ctx.obj["url"]
    
    async def get_stats():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/api/stats")
            response.raise_for_status()
            return response.json()
    
    result = asyncio.run(get_stats())
    
    # Query Statistics
    console.print(Panel("Query Statistics", style="bold blue"))
    query_stats = result.get("query_stats", {})
    console.print(f"Total Queries: {query_stats.get('total_queries', 0)}")
    console.print(f"Average Latency: {query_stats.get('average_latency', 0):.2f}s")
    console.print(f"Cache Hit Rate: {query_stats.get('cache_hit_rate', 0):.2%}")
    
    # Document Statistics
    console.print("\n")
    console.print(Panel("Document Processing Statistics", style="bold green"))
    doc_stats = result.get("document_stats", {})
    console.print(f"Total Processed: {doc_stats.get('total_processed', 0)}")
    console.print(f"Success Rate: {doc_stats.get('success_rate', 0):.2%}")
    console.print(f"Average Time: {doc_stats.get('average_processing_time', 0):.2f}s")
    
    # Workflow Statistics
    console.print("\n")
    console.print(Panel("Workflow Statistics", style="bold yellow"))
    workflow_stats = result.get("workflow_stats", {})
    console.print(f"Total Deployments: {workflow_stats.get('total_deployments', 0)}")
    console.print(f"Total Executions: {workflow_stats.get('total_executions', 0)}")
    console.print(f"Success Rate: {workflow_stats.get('success_rate', 0):.2%}")


@cli.command()
@click.argument("query")
@click.pass_context
def analyze(ctx, query):
    """Analyze a query to see routing recommendations"""
    url = ctx.obj["url"]
    
    async def analyze_query():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{url}/api/query/analyze",
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
    
    result = asyncio.run(analyze_query())
    
    console.print(Panel(f"Query: {result['query']}", title="Query Analysis"))
    
    analysis = result["analysis"]
    console.print(f"\n[bold]Query Type:[/bold] {analysis.get('query_type', 'unknown')}")
    console.print(f"[bold]Complexity:[/bold] {analysis.get('complexity', 'unknown')}")
    console.print(f"[bold]Requires Context:[/bold] {analysis.get('requires_context', False)}")
    console.print(f"[bold]Broad Search:[/bold] {analysis.get('broad_search', False)}")
    
    console.print(f"\n[bold]Recommended Mode:[/bold] {result['recommended_mode']}")
    console.print(f"[bold]Recommended Sources:[/bold] {', '.join(result['recommended_sources'])}")
    
    if analysis.get('features_needed'):
        console.print(f"\n[bold]Features Needed:[/bold]")
        for feature in analysis['features_needed']:
            console.print(f"  - {feature}")


if __name__ == "__main__":
    cli()