"""Workflow service - bridges API to existing WorkflowExecutor."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os

from agents.workflow_executor import WorkflowExecutor, WorkflowRequest
from agents.base.models import ContentType, ToneType

from api.schemas.workflow import (
    WorkflowRequestSchema,
    WorkflowResultResponse,
    WorkflowJobStatus,
    WorkflowStepProgress,
    OutputFileInfo,
)
from api.config import settings

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service layer bridging API to existing WorkflowExecutor."""

    def __init__(self):
        """Initialize workflow service."""
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    def _get_executor(self, brand_template: str = "professional") -> WorkflowExecutor:
        """Get workflow executor with configuration."""
        config = {
            "production": {
                "output_dir": settings.OUTPUT_DIR,
                "brand_template": brand_template,  # Pass string name, not object
            }
        }
        return WorkflowExecutor(config)

    def _convert_request(self, schema: WorkflowRequestSchema) -> WorkflowRequest:
        """Convert API schema to internal WorkflowRequest."""
        # Map content types
        content_types = [
            ContentType(ct.value) for ct in schema.content_types
        ]

        # Build additional context
        additional_context: Dict[str, Any] = {
            "target_audience": schema.target_audience,
            "tone": ToneType(schema.tone.value),
            "output_format": schema.output_format.value,
            "include_metadata": schema.include_metadata,
            "page_numbers": schema.page_numbers,
        }

        # Add word count if specified
        if schema.word_count_min and schema.word_count_max:
            additional_context["word_count_range"] = (
                schema.word_count_min,
                schema.word_count_max,
            )

        # Add social settings if present
        if schema.social_settings:
            additional_context["social"] = {
                "platform": schema.social_settings.platform.value,
                "format_type": schema.social_settings.format_type,
                "include_cta": schema.social_settings.include_cta,
                "emoji_density": schema.social_settings.emoji_density,
            }

        return WorkflowRequest(
            request_text=schema.request_text,
            content_types=content_types,
            priority=schema.priority.value,
            deadline=schema.deadline.isoformat() if schema.deadline else None,
            additional_context=additional_context,
        )

    async def execute_workflow_async(
        self,
        job_id: str,
        request: WorkflowRequestSchema,
        jobs: Dict[str, Any],
    ):
        """Execute workflow asynchronously and update job status."""
        try:
            # Update status to running
            jobs[job_id]["status"] = WorkflowJobStatus.RUNNING
            jobs[job_id]["current_step"] = "Converting request"
            jobs[job_id]["progress"] = 10
            self._add_step_progress(jobs[job_id], "initialization", "started")

            # Get executor with brand template
            executor = self._get_executor(request.brand_template)

            # Convert request
            workflow_request = self._convert_request(request)

            jobs[job_id]["current_step"] = "Executing workflow"
            jobs[job_id]["progress"] = 20
            self._add_step_progress(jobs[job_id], "conversion", "completed")

            # Execute workflow (synchronous in current implementation)
            result = executor.execute(workflow_request)

            # Update progress based on steps completed
            total_steps = len(result.steps_completed)
            for i, step in enumerate(result.steps_completed):
                progress = 20 + int(70 * (i + 1) / max(total_steps, 1))
                jobs[job_id]["progress"] = min(progress, 90)
                self._add_step_progress(
                    jobs[job_id],
                    step["step"],
                    "completed" if step["success"] else "failed",
                    step.get("error"),
                )

            # Process result
            if result.success:
                jobs[job_id]["status"] = WorkflowJobStatus.COMPLETED
                jobs[job_id]["progress"] = 100
                jobs[job_id]["current_step"] = "Completed"

                # Build output file info
                outputs = []
                if "production_outputs" in result.outputs:
                    for i, output in enumerate(result.outputs["production_outputs"]):
                        file_path = output.file_path
                        file_size = 0
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)

                        outputs.append(
                            OutputFileInfo(
                                file_id=f"{i}",
                                filename=os.path.basename(file_path),
                                format=output.file_format,
                                size_bytes=file_size,
                                download_url=f"/api/workflow/download/{job_id}/{i}",
                            )
                        )

                # Extract content preview
                content_preview = None
                if "draft_content" in result.outputs:
                    draft = result.outputs["draft_content"]
                    if hasattr(draft, "content"):
                        content_preview = draft.content[:500] + "..." if len(draft.content) > 500 else draft.content

                jobs[job_id]["result"] = WorkflowResultResponse(
                    job_id=job_id,
                    status=WorkflowJobStatus.COMPLETED,
                    workflow_type=result.workflow_type,
                    success=True,
                    outputs=outputs,
                    content_preview=content_preview,
                    metadata={
                        "steps_completed": len(result.steps_completed),
                        "content_types": [ct.value for ct in workflow_request.content_types],
                    },
                    start_time=datetime.fromisoformat(result.start_time),
                    end_time=datetime.fromisoformat(result.end_time) if result.end_time else None,
                )

                # Store production outputs for download
                if "production_outputs" in result.outputs:
                    jobs[job_id]["files"] = result.outputs["production_outputs"]

            else:
                jobs[job_id]["status"] = WorkflowJobStatus.FAILED
                jobs[job_id]["error"] = "; ".join(result.errors)
                jobs[job_id]["result"] = WorkflowResultResponse(
                    job_id=job_id,
                    status=WorkflowJobStatus.FAILED,
                    workflow_type=result.workflow_type,
                    success=False,
                    errors=result.errors,
                    start_time=datetime.fromisoformat(result.start_time),
                    end_time=datetime.fromisoformat(result.end_time) if result.end_time else None,
                )

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            jobs[job_id]["status"] = WorkflowJobStatus.FAILED
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["result"] = WorkflowResultResponse(
                job_id=job_id,
                status=WorkflowJobStatus.FAILED,
                workflow_type="unknown",
                success=False,
                errors=[str(e)],
                start_time=datetime.now(),
            )

    def _add_step_progress(
        self,
        job: Dict[str, Any],
        step: str,
        status: str,
        message: Optional[str] = None,
    ):
        """Add step progress to job."""
        job["steps_completed"].append(
            WorkflowStepProgress(
                step=step,
                status=status,
                timestamp=datetime.now(),
                message=message,
            )
        )
