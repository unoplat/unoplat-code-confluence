from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from temporalio.client import Client
import asyncio

app = FastAPI(title="Code Confluence Flow Bridge")

class DraftConfiguration(BaseModel):
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    task_queue: str = Field(..., description="Task queue name for the workflow")
    configuration: Dict[str, Any] = Field(..., description="Configuration parameters for the workflow")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Optional metadata for the workflow")

async def get_temporal_client() -> Client:
    """Create and return a Temporal client instance."""
    # Connect to local temporal server
    client = await Client.connect("localhost:7233")
    return client

@app.post("/drafts", status_code=201)
async def create_draft(config: DraftConfiguration):
    """
    Create a new draft configuration and submit it to Temporal workflow.
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
            "message": "Draft configuration submitted successfully",
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