"""
Workflow Executor - Executes complete workflows end-to-end.

Orchestrates the execution of multi-step workflows by coordinating
agents and skills, managing state, and enforcing quality gates.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from agents.base.models import (
    WorkflowRequest, ResearchBrief, ContentBrief, DraftContent,
    BrandVoiceResult, ProductionOutput, ContentType
)
from agents.orchestrator.orchestrator import OrchestratorAgent, WorkflowType
from agents.research.research import ResearchAgent
from agents.creation.creation import CreationAgent
from agents.production.production import ProductionAgent
from skills.content_brief.content_brief import ContentBriefSkill
from skills.brand_voice.brand_voice import BrandVoiceSkill


class WorkflowExecutionResult:
    """Result of workflow execution."""

    def __init__(self, workflow_type: str, success: bool):
        self.workflow_type = workflow_type
        self.success = success
        self.steps_completed: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.outputs: Dict[str, Any] = {}
        self.start_time = datetime.now().isoformat()
        self.end_time: Optional[str] = None

    def add_step(self, step_name: str, output: Any, success: bool, error: Optional[str] = None):
        """Record a completed step."""
        self.steps_completed.append({
            "step": step_name,
            "success": success,
            "output_type": type(output).__name__ if output else None,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        if error:
            self.errors.append(f"{step_name}: {error}")

    def finalize(self, success: bool):
        """Mark workflow as complete."""
        self.success = success
        self.end_time = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_type": self.workflow_type,
            "success": self.success,
            "steps_completed": self.steps_completed,
            "errors": self.errors,
            "outputs": self.outputs,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class WorkflowExecutor:
    """
    Executes complete workflows from request to output.

    Coordinates orchestrator, agents, and skills to execute
    multi-step content creation workflows with quality gates.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize workflow executor.

        Args:
            config: Optional configuration for agents and skills
        """
        self.config = config or {}
        self.logger = logging.getLogger("workflow_executor")

        # Initialize components
        self.orchestrator = OrchestratorAgent(self.config.get("orchestrator"))
        self.research_agent = ResearchAgent(self.config.get("research"))
        self.creation_agent = CreationAgent(self.config.get("creation"))
        self.production_agent = ProductionAgent(self.config.get("production"))
        self.content_brief_skill = ContentBriefSkill(self.config.get("content_brief"))
        self.brand_voice_skill = BrandVoiceSkill(self.config.get("brand_voice"))

        # Execution settings
        self.max_retries = self.config.get("max_retries", 3)
        self.enforce_quality_gates = self.config.get("enforce_quality_gates", True)

    def execute(self, request: WorkflowRequest) -> WorkflowExecutionResult:
        """
        Execute a workflow from start to finish.

        Args:
            request: WorkflowRequest from user

        Returns:
            WorkflowExecutionResult with outputs and status
        """
        self.logger.info(f"Executing workflow for: {request.request_text}")

        # Step 1: Plan workflow
        plan = self.orchestrator.process(request)
        workflow_type = plan["workflow_type"]
        execution_plan = plan["execution_plan"]

        result = WorkflowExecutionResult(workflow_type, False)

        self.logger.info(f"Workflow: {workflow_type} with {len(execution_plan)} steps")

        try:
            # Execute based on workflow type
            if workflow_type == WorkflowType.ARTICLE_PRODUCTION:
                self._execute_article_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.MULTI_PLATFORM_CAMPAIGN:
                self._execute_multi_platform_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.SOCIAL_ONLY:
                self._execute_social_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.EMAIL_SEQUENCE:
                self._execute_email_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.PRESENTATION:
                self._execute_presentation_workflow(request, execution_plan, result)
            else:
                raise ValueError(f"Unsupported workflow type: {workflow_type}")

            result.finalize(True)
            self.logger.info(f"Workflow completed successfully")

        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            result.add_step("workflow_execution", None, False, str(e))
            result.finalize(False)

        return result

    def _execute_article_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute article production workflow."""

        # Step 1: Research
        self.logger.info("Step 1/5: Research")
        research_brief = self._execute_research(request.request_text, result)
        result.outputs["research_brief"] = research_brief

        # Step 2: Content Brief
        self.logger.info("Step 2/5: Content Brief")
        content_brief = self._execute_content_brief(
            research_brief,
            request.content_types[0],
            request.additional_context,
            result
        )
        result.outputs["content_brief"] = content_brief

        # Step 3: Creation
        self.logger.info("Step 3/5: Creation")
        draft = self._execute_creation(content_brief, result)
        result.outputs["draft_content"] = draft

        # Step 4: Brand Voice
        self.logger.info("Step 4/5: Brand Voice Validation")
        brand_result = self._execute_brand_voice(draft, content_brief.tone, result)
        result.outputs["brand_voice_result"] = brand_result

        # Step 5: Production
        self.logger.info("Step 5/5: Production")
        output_format = request.additional_context.get("output_format", "html")
        self._execute_production(draft, output_format, result)

    def _execute_multi_platform_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute multi-platform campaign workflow."""

        # Step 1: Research (shared)
        self.logger.info("Step 1: Research (shared)")
        research_brief = self._execute_research(request.request_text, result)
        result.outputs["research_brief"] = research_brief

        # Step 2: Content Briefs (one per platform)
        self.logger.info("Step 2: Create Content Briefs")
        briefs = []
        for content_type in request.content_types:
            brief = self._execute_content_brief(
                research_brief,
                content_type,
                request.additional_context,
                result
            )
            briefs.append(brief)
        result.outputs["content_briefs"] = briefs

        # Step 3: Creation (parallel - but sequential in Phase 2)
        self.logger.info("Step 3: Content Creation (multi-format)")
        drafts = []
        for brief in briefs:
            draft = self._execute_creation(brief, result)
            drafts.append(draft)
        result.outputs["drafts"] = drafts

        # Step 4: Brand Voice (validate all)
        self.logger.info("Step 4: Brand Voice Validation (all formats)")
        brand_results = []
        for draft in drafts:
            brand_result = self._execute_brand_voice(
                draft,
                briefs[0].tone,  # Use first brief's tone
                result
            )
            brand_results.append(brand_result)
        result.outputs["brand_voice_results"] = brand_results

        # Step 5: Production (multi-format)
        self.logger.info("Step 5: Production (multi-format)")
        output_formats = request.additional_context.get("output_formats", ["html"])
        for draft in drafts:
            if isinstance(output_formats, list) and len(output_formats) > 1:
                self._produce_multiple_formats(draft, output_formats, result)
            else:
                fmt = output_formats[0] if isinstance(output_formats, list) else output_formats
                self._execute_production(draft, fmt, result)

    def _execute_social_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute social-only workflow."""
        # Similar to article but optimized for social
        self._execute_article_workflow(request, execution_plan, result)

    def _execute_email_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute email sequence workflow."""
        # Similar to article but for email format
        self._execute_article_workflow(request, execution_plan, result)

    def _execute_presentation_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute presentation workflow."""
        # Similar to article but for presentation format
        self._execute_article_workflow(request, execution_plan, result)

    def _execute_research(self, topic: str, result: WorkflowExecutionResult) -> ResearchBrief:
        """Execute research step with quality gate."""
        try:
            research_brief = self.research_agent.process({"topic": topic})

            # Quality Gate 1: Research Completeness
            if self.enforce_quality_gates:
                is_valid, errors = research_brief.validate()
                if not is_valid:
                    error_msg = f"Research quality gate failed: {errors}"
                    self.logger.warning(error_msg)
                    result.add_step("research", research_brief, False, error_msg)
                    if self.config.get("strict_quality_gates"):
                        raise ValueError(error_msg)

            result.add_step("research", research_brief, True)
            return research_brief

        except Exception as e:
            result.add_step("research", None, False, str(e))
            raise

    def _execute_content_brief(
        self,
        research_brief: ResearchBrief,
        content_type: ContentType,
        additional_context: Dict[str, Any],
        result: WorkflowExecutionResult
    ) -> ContentBrief:
        """Execute content brief creation with quality gate."""
        try:
            content_brief = self.content_brief_skill.execute(
                research_brief=research_brief,
                content_type=content_type,
                target_audience=additional_context.get("target_audience"),
                additional_requirements=additional_context
            )

            # Quality Gate 2: Brief Alignment
            if self.enforce_quality_gates:
                is_valid, errors = content_brief.validate()
                if not is_valid:
                    error_msg = f"Brief quality gate failed: {errors}"
                    self.logger.warning(error_msg)
                    result.add_step("content_brief", content_brief, False, error_msg)
                    if self.config.get("strict_quality_gates"):
                        raise ValueError(error_msg)

            result.add_step("content_brief", content_brief, True)
            return content_brief

        except Exception as e:
            result.add_step("content_brief", None, False, str(e))
            raise

    def _execute_creation(
        self,
        content_brief: ContentBrief,
        result: WorkflowExecutionResult
    ) -> DraftContent:
        """Execute content creation."""
        try:
            draft = self.creation_agent.process({"content_brief": content_brief})

            # Basic validation
            is_valid, errors = draft.validate()
            if not is_valid:
                self.logger.warning(f"Draft validation issues: {errors}")

            result.add_step("creation", draft, True)
            return draft

        except Exception as e:
            result.add_step("creation", None, False, str(e))
            raise

    def _execute_brand_voice(
        self,
        draft: DraftContent,
        target_tone: Any,
        result: WorkflowExecutionResult
    ) -> BrandVoiceResult:
        """Execute brand voice validation with quality gate."""
        try:
            brand_result = self.brand_voice_skill.execute(
                draft_content=draft,
                target_tone=target_tone
            )

            # Quality Gate 3: Brand Consistency
            if self.enforce_quality_gates:
                is_valid, errors = brand_result.validate()
                if not is_valid:
                    error_msg = f"Brand voice quality gate failed: {errors}"
                    self.logger.warning(error_msg)
                    result.add_step("brand_voice", brand_result, False, error_msg)
                    if self.config.get("strict_quality_gates"):
                        raise ValueError(error_msg)

            result.add_step("brand_voice", brand_result, True)
            return brand_result

        except Exception as e:
            result.add_step("brand_voice", None, False, str(e))
            raise

    def _execute_production(
        self,
        draft: DraftContent,
        output_format: str,
        result: WorkflowExecutionResult,
        template_override: Optional[str] = None
    ):
        """Execute production step to generate final output."""
        try:
            output = self.production_agent.process({
                "draft_content": draft,
                "output_format": output_format,
                "template_override": template_override
            })

            result.add_step("production", output, True)
            if "production_outputs" not in result.outputs:
                result.outputs["production_outputs"] = []
            result.outputs["production_outputs"].append(output)

            self.logger.info(f"Produced {output.file_format} file: {output.file_path}")

        except Exception as e:
            result.add_step("production", None, False, str(e))
            raise

    def _produce_multiple_formats(
        self,
        draft: DraftContent,
        formats: List[str],
        result: WorkflowExecutionResult,
        template_override: Optional[str] = None
    ):
        """Produce content in multiple formats."""
        try:
            outputs = self.production_agent.batch_produce(
                [draft],
                formats,
                template_override=template_override
            )

            for output in outputs:
                result.add_step(f"production_{output.file_format}", output, True)

            if "production_outputs" not in result.outputs:
                result.outputs["production_outputs"] = []
            result.outputs["production_outputs"].extend(outputs)

            self.logger.info(f"Produced {len(outputs)} files in formats: {', '.join(formats)}")

        except Exception as e:
            result.add_step("batch_production", None, False, str(e))
            raise
