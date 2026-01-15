"""Workflow API router."""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import FileResponse
from typing import Dict
import uuid
from datetime import datetime
import os

from api.schemas.workflow import (
    WorkflowRequestSchema,
    WorkflowStatusResponse,
    WorkflowResultResponse,
    WorkflowJobStatus,
)
from api.services.workflow_service import WorkflowService

router = APIRouter()

# In-memory job store (use Redis in production)
jobs: Dict[str, dict] = {}


def get_workflow_service(request: Request) -> WorkflowService:
    """Dependency to get workflow service."""
    return request.app.state.workflow_service


@router.post("/execute", response_model=WorkflowStatusResponse)
async def execute_workflow(
    request: WorkflowRequestSchema,
    background_tasks: BackgroundTasks,
    service: WorkflowService = Depends(get_workflow_service),
):
    """
    Submit a workflow for execution.

    Returns immediately with a job_id for status tracking.
    Workflow executes asynchronously in the background.
    """
    job_id = str(uuid.uuid4())

    # Initialize job status
    jobs[job_id] = {
        "status": WorkflowJobStatus.PENDING,
        "progress": 0,
        "current_step": "Queued",
        "steps_completed": [],
        "result": None,
        "error": None,
        "files": [],
        "created_at": datetime.now(),
    }

    # Execute workflow in background
    background_tasks.add_task(
        service.execute_workflow_async,
        job_id,
        request,
        jobs,
    )

    return WorkflowStatusResponse(
        job_id=job_id,
        status=WorkflowJobStatus.PENDING,
        progress=0,
        current_step="Initializing workflow",
    )


@router.get("/status/{job_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(job_id: str):
    """Get current status of a workflow job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return WorkflowStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        steps_completed=job["steps_completed"],
        error_message=job.get("error"),
    )


@router.get("/result/{job_id}", response_model=WorkflowResultResponse)
async def get_workflow_result(job_id: str):
    """Get final result of a completed workflow."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] not in [WorkflowJobStatus.COMPLETED, WorkflowJobStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Workflow not yet complete. Status: {job['status'].value}",
        )

    if job["result"] is None:
        raise HTTPException(
            status_code=500,
            detail="Workflow completed but result is missing",
        )

    return job["result"]


@router.get("/download/{job_id}/{file_id}")
async def download_file(job_id: str, file_id: str):
    """Download a generated output file."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != WorkflowJobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Workflow not completed",
        )

    try:
        file_index = int(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID")

    files = job.get("files", [])
    if file_index < 0 or file_index >= len(files):
        raise HTTPException(status_code=404, detail="File not found")

    output = files[file_index]
    file_path = output.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream",
    )


@router.get("/jobs")
async def list_jobs():
    """List all workflow jobs (for debugging)."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"].value,
                "progress": job["progress"],
                "created_at": job["created_at"].isoformat(),
            }
            for job_id, job in jobs.items()
        ]
    }
