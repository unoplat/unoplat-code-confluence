from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.code_confluence_flow_bridge.models.configuration.settings import AppConfig
from temporalio.client import Client
import asyncio

app = FastAPI(title="Code Confluence Flow Bridge")


async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    client = await Client.connect("localhost:7233")
    return client

@app.post("/start-ingestion", status_code=201)
async def start_ingestion(config: AppConfig):
    """
    Start the ingestion workflow.
    """
    try:
        # Get temporal client
        client = await get_temporal_client()
        
        # Here we'll need to start the workflow
        # This is a placeholder for the actual workflow execution
        # await client.start_workflow(
        #     "workflow_name",
        #     config.configuration,
        #     id=config.workflow_id,
        #     task_queue=config.task_queue,
        # )

        return {
            "status": "success",
            "message": "Ingestion workflow started successfully",
            "workflow_id": config.workflow_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit draft configuration: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Code Confluence Flow Bridge API",
        "version": "1.0.0"
    }