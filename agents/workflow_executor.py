"""
Workflow Executor - Executes complete workflows end-to-end.

Orchestrates the execution of multi-step workflows by coordinating
agents and skills, managing state, and enforcing quality gates.

Phase 4: Multi-platform workflows execute content creation in parallel
using asyncio.gather for improved throughput.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from agents.base.models import (
    WorkflowRequest, ResearchBrief, ContentBrief, DraftContent,
    BrandVoiceResult, ProductionOutput, ContentType
)
from agents.orchestrator.orchestrator import OrchestratorAgent, WorkflowType
from agents.research.research import ResearchAgent
from agents.research.llm_research import LLMResearchAgent
from agents.creation.creation import CreationAgent
from agents.creation.llm_creation import LLMCreationAgent
from agents.production.production import ProductionAgent
from skills.content_brief.content_brief import ContentBriefSkill
from skills.brand_voice.brand_voice import BrandVoiceSkill
from skills.email_generation.email_generation import EmailGenerationSkill


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

    Phase 4: Multi-platform workflows run content creation in parallel.
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
        self.production_agent = ProductionAgent(self.config.get("production"))
        self.content_brief_skill = ContentBriefSkill(self.config.get("content_brief"))
        self.brand_voice_skill = BrandVoiceSkill(self.config.get("brand_voice"))
        self.email_skill = EmailGenerationSkill(self.config.get("email_generation"))

        # Use LLM-powered agents when a model registry is configured;
        # fall back to mock/template agents when no API keys are available.
        self.research_agent = self._init_research_agent()
        self.creation_agent = self._init_creation_agent()

        # Execution settings
        self.max_retries = self.config.get("max_retries", 3)
        self.enforce_quality_gates = self.config.get("enforce_quality_gates", True)

    def _get_registry_if_configured(self):
        """Return the model registry only if at least one LLM provider is configured."""
        try:
            from core.models import get_registry
            registry = get_registry()
            if registry.list_providers():
                return registry
        except Exception:
            pass
        return None

    def _init_research_agent(self):
        """Return LLMResearchAgent if an LLM provider is configured, else mock ResearchAgent."""
        registry = self._get_registry_if_configured()
        if registry:
            self.logger.info("Using LLMResearchAgent")
            return LLMResearchAgent(config=self.config.get("research"), registry=registry)
        self.logger.warning("No LLM provider configured — using mock ResearchAgent")
        return ResearchAgent(self.config.get("research"))

    def _init_creation_agent(self):
        """Return LLMCreationAgent if an LLM provider is configured, else mock CreationAgent."""
        registry = self._get_registry_if_configured()
        if registry:
            self.logger.info("Using LLMCreationAgent")
            return LLMCreationAgent(config=self.config.get("creation"), registry=registry)
        self.logger.warning("No LLM provider configured — using mock CreationAgent")
        return CreationAgent(self.config.get("creation"))

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
            if workflow_type == WorkflowType.ARTICLE_PRODUCTION:
                self._execute_article_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.MULTI_PLATFORM_CAMPAIGN:
                # Run parallel creation via asyncio
                asyncio.run(self._execute_multi_platform_workflow_async(request, execution_plan, result))
            elif workflow_type == WorkflowType.SOCIAL_ONLY:
                self._execute_social_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.EMAIL_SEQUENCE:
                self._execute_email_workflow(request, execution_plan, result)
            elif workflow_type == WorkflowType.PRESENTATION:
                self._execute_presentation_workflow(request, execution_plan, result)
            else:
                raise ValueError(f"Unsupported workflow type: {workflow_type}")

            result.finalize(True)
            self.logger.info("Workflow completed successfully")

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
        self.logger.info("Step 1/5: Research")
        source_urls = request.additional_context.get("source_urls")
        research_brief = self._execute_research(request.request_text, result, source_urls)
        result.outputs["research_brief"] = research_brief

        self.logger.info("Step 2/5: Content Brief")
        content_brief = self._execute_content_brief(
            research_brief, request.content_types[0], request.additional_context, result
        )
        result.outputs["content_brief"] = content_brief

        self.logger.info("Step 3/5: Creation")
        draft = self._execute_creation(content_brief, result)
        result.outputs["draft_content"] = draft

        self.logger.info("Step 4/5: Brand Voice Validation")
        brand_result = self._execute_brand_voice(draft, content_brief.tone, result)
        result.outputs["brand_voice_result"] = brand_result

        self.logger.info("Step 5/5: Production")
        output_format = request.additional_context.get("output_format", "html")
        self._execute_production(draft, output_format, result)

    async def _execute_multi_platform_workflow_async(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute multi-platform campaign workflow with parallel content creation."""

        # Step 1: Research (shared, sequential)
        self.logger.info("Step 1: Research (shared)")
        source_urls = request.additional_context.get("source_urls")
        research_brief = self._execute_research(request.request_text, result, source_urls)
        result.outputs["research_brief"] = research_brief

        # Step 2: Content Briefs (sequential, fast)
        self.logger.info("Step 2: Create Content Briefs")
        briefs = []
        for content_type in request.content_types:
            brief = self._execute_content_brief(
                research_brief, content_type, request.additional_context, result
            )
            briefs.append(brief)
        result.outputs["content_briefs"] = briefs

        # Step 3: Creation (PARALLEL via asyncio.gather)
        self.logger.info(f"Step 3: Content Creation (parallel x{len(briefs)})")
        draft_tasks = [self._execute_creation_async(brief, result) for brief in briefs]
        drafts = await asyncio.gather(*draft_tasks, return_exceptions=True)

        # Filter out exceptions and log them
        valid_drafts = []
        for i, draft in enumerate(drafts):
            if isinstance(draft, Exception):
                self.logger.error(f"Draft {i} failed: {draft}")
                result.add_step(f"creation_{i}", None, False, str(draft))
            else:
                valid_drafts.append(draft)
        drafts = valid_drafts
        result.outputs["drafts"] = drafts

        # Step 4: Brand Voice (parallel)
        self.logger.info("Step 4: Brand Voice Validation (parallel)")
        bv_tasks = [
            self._execute_brand_voice_async(draft, briefs[0].tone, result)
            for draft in drafts
        ]
        brand_results = await asyncio.gather(*bv_tasks, return_exceptions=True)
        result.outputs["brand_voice_results"] = [r for r in brand_results if not isinstance(r, Exception)]

        # Step 5: Production (parallel)
        self.logger.info("Step 5: Production (multi-format)")
        output_formats = request.additional_context.get("output_formats", ["html"])
        prod_tasks = []
        for draft in drafts:
            if isinstance(output_formats, list) and len(output_formats) > 1:
                prod_tasks.append(self._produce_multiple_formats_async(draft, output_formats, result))
            else:
                fmt = output_formats[0] if isinstance(output_formats, list) else output_formats
                prod_tasks.append(self._execute_production_async(draft, fmt, result))
        await asyncio.gather(*prod_tasks, return_exceptions=True)

    def _execute_social_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute social-only workflow (article pipeline, social output format)."""
        self._execute_article_workflow(request, execution_plan, result)

    def _execute_email_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute email sequence workflow with dedicated email generation."""

        # Step 1: Research
        self.logger.info("Step 1/4: Research")
        source_urls = request.additional_context.get("source_urls")
        research_brief = self._execute_research(request.request_text, result, source_urls)
        result.outputs["research_brief"] = research_brief

        # Step 2: Content Brief
        self.logger.info("Step 2/4: Content Brief")
        content_type = request.content_types[0] if request.content_types else ContentType.EMAIL
        content_brief = self._execute_content_brief(
            research_brief, content_type, request.additional_context, result
        )
        result.outputs["content_brief"] = content_brief

        # Step 3: Email Generation
        self.logger.info("Step 3/4: Email Generation")
        email_type = request.additional_context.get("email_type", "newsletter")
        try:
            email_content = self.email_skill.execute(
                content_brief=content_brief,
                email_type=email_type,
                recipient_context=request.additional_context.get("target_audience"),
                sender_name=request.additional_context.get("sender_name", ""),
                company_name=request.additional_context.get("company_name", ""),
            )
            result.add_step("email_generation", email_content, True)

            # Convert to DraftContent for production
            draft = DraftContent(
                content=email_content.to_full_text(),
                content_type=ContentType.EMAIL,
                word_count=email_content.word_count,
                metadata={
                    "subject": email_content.subject,
                    "preview_text": email_content.preview_text,
                    "email_type": email_type,
                }
            )
            result.outputs["draft_content"] = draft
            result.outputs["email_content"] = email_content

        except Exception as e:
            result.add_step("email_generation", None, False, str(e))
            raise

        # Step 4: Production (HTML output for email)
        self.logger.info("Step 4/4: Production")
        output_format = request.additional_context.get("output_format", "html")
        self._execute_production(draft, output_format, result)

    def _execute_presentation_workflow(
        self,
        request: WorkflowRequest,
        execution_plan: List[Dict[str, Any]],
        result: WorkflowExecutionResult
    ):
        """Execute presentation workflow (article pipeline → PPTX)."""
        # Force PPTX output for presentation workflows
        request.additional_context.setdefault("output_format", "pptx")
        self._execute_article_workflow(request, execution_plan, result)

    # ------------------------------------------------------------------
    # Step executors (sync)
    # ------------------------------------------------------------------

    def _execute_research(
        self,
        topic: str,
        result: WorkflowExecutionResult,
        source_urls: Optional[List[str]] = None,
    ) -> ResearchBrief:
        """Execute research step with quality gate."""
        try:
            input_data = {"topic": topic}
            if source_urls:
                input_data["source_urls"] = source_urls
            research_brief = self.research_agent.process(input_data)

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
            is_valid, errors = draft.validate()
            if not is_valid:
                self.logger.warning(f"Draft validation issues: {errors}")
            result.add_step("creation", draft, True)
            return draft
        except Exception as e:
            result.add_step("creation", None, False, str(e))
            raise

    async def _execute_creation_async(
        self,
        content_brief: ContentBrief,
        result: WorkflowExecutionResult
    ) -> DraftContent:
        """Async wrapper for content creation (runs sync in thread pool)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._execute_creation, content_brief, result
        )

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

    async def _execute_brand_voice_async(
        self,
        draft: DraftContent,
        target_tone: Any,
        result: WorkflowExecutionResult
    ) -> BrandVoiceResult:
        """Async wrapper for brand voice validation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._execute_brand_voice, draft, target_tone, result
        )

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

    async def _execute_production_async(
        self,
        draft: DraftContent,
        output_format: str,
        result: WorkflowExecutionResult,
        template_override: Optional[str] = None
    ):
        """Async wrapper for production."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._execute_production, draft, output_format, result, template_override
        )

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
                [draft], formats, template_override=template_override
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

    async def _produce_multiple_formats_async(
        self,
        draft: DraftContent,
        formats: List[str],
        result: WorkflowExecutionResult,
        template_override: Optional[str] = None
    ):
        """Async wrapper for batch production."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._produce_multiple_formats, draft, formats, result, template_override
        )
