"""
Orchestrator Agent - Central coordinator for content creation workflows.

Routes requests to appropriate agents and manages workflow execution.
"""

from typing import Dict, List, Any, Optional
from agents.base.agent import Agent
from agents.base.models import (
    WorkflowRequest, ContentType, ContentBrief, ResearchBrief,
    DraftContent, ProductionOutput
)


class WorkflowType:
    """Workflow type definitions."""
    ARTICLE_PRODUCTION = "article_production"
    MULTI_PLATFORM_CAMPAIGN = "multi_platform_campaign"
    PRESENTATION = "presentation"
    SOCIAL_ONLY = "social_only"
    EMAIL_SEQUENCE = "email_sequence"


class OrchestratorAgent(Agent):
    """
    Central coordinator that routes requests and manages workflows.

    Responsibilities:
    - Parse content requests into discrete tasks
    - Select appropriate workflow and agent sequence
    - Manage state between agent handoffs
    - Aggregate outputs into cohesive deliverables
    - Handle retries and quality gates
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("orchestrator", config)
        self.workflows = self._initialize_workflows()

    def _initialize_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Define available workflow patterns."""
        return {
            WorkflowType.ARTICLE_PRODUCTION: {
                "description": "Single article/blog post production",
                "sequence": ["research", "content_brief", "creation", "brand_voice", "production"],
                "content_types": [ContentType.ARTICLE, ContentType.BLOG_POST],
                "parallel": False
            },
            WorkflowType.MULTI_PLATFORM_CAMPAIGN: {
                "description": "Content for multiple platforms from single research",
                "sequence": ["research", "content_brief", "creation_parallel", "brand_voice", "production"],
                "content_types": [ContentType.ARTICLE, ContentType.SOCIAL_POST, ContentType.EMAIL],
                "parallel": True
            },
            WorkflowType.PRESENTATION: {
                "description": "Presentation from research or existing content",
                "sequence": ["research", "content_brief", "creation", "production"],
                "content_types": [ContentType.PRESENTATION],
                "parallel": False
            },
            WorkflowType.SOCIAL_ONLY: {
                "description": "Social media content only",
                "sequence": ["research", "content_brief", "creation", "brand_voice"],
                "content_types": [ContentType.SOCIAL_POST],
                "parallel": False
            },
            WorkflowType.EMAIL_SEQUENCE: {
                "description": "Email campaign or sequence",
                "sequence": ["research", "content_brief", "creation", "brand_voice", "production"],
                "content_types": [ContentType.EMAIL, ContentType.NEWSLETTER],
                "parallel": False
            }
        }

    def process(self, input_data: WorkflowRequest) -> Dict[str, Any]:
        """
        Process a workflow request.

        Args:
            input_data: WorkflowRequest from user

        Returns:
            Workflow execution result
        """
        self.logger.info(f"Processing request: {input_data.request_text}")

        # Step 1: Determine workflow type
        workflow_type = self._determine_workflow_type(input_data)
        self.logger.info(f"Selected workflow: {workflow_type}")

        # Step 2: Parse requirements
        requirements = self._parse_request(input_data)

        # Step 3: Create execution plan
        execution_plan = self._create_execution_plan(workflow_type, requirements)

        # Step 4: Execute workflow (stub for Phase 1)
        result = {
            "workflow_type": workflow_type,
            "workflow_description": self.workflows[workflow_type]["description"],
            "execution_plan": execution_plan,
            "requirements": requirements,
            "status": "planned",
            "message": "Workflow planned successfully (execution in later phases)"
        }

        self.log_execution(input_data, result)
        return result

    def _determine_workflow_type(self, request: WorkflowRequest) -> str:
        """
        Analyze request to determine appropriate workflow.

        Args:
            request: User's workflow request

        Returns:
            Workflow type identifier
        """
        content_types = request.content_types

        # Multi-platform campaign
        if len(content_types) > 1:
            return WorkflowType.MULTI_PLATFORM_CAMPAIGN

        # Single content type workflows
        content_type = content_types[0]

        if content_type in [ContentType.ARTICLE, ContentType.BLOG_POST, ContentType.WHITEPAPER, ContentType.CASE_STUDY]:
            return WorkflowType.ARTICLE_PRODUCTION
        elif content_type == ContentType.PRESENTATION:
            return WorkflowType.PRESENTATION
        elif content_type == ContentType.SOCIAL_POST:
            return WorkflowType.SOCIAL_ONLY
        elif content_type in [ContentType.EMAIL, ContentType.NEWSLETTER]:
            return WorkflowType.EMAIL_SEQUENCE
        else:
            # Default to article production
            return WorkflowType.ARTICLE_PRODUCTION

    def _parse_request(self, request: WorkflowRequest) -> Dict[str, Any]:
        """
        Extract requirements from request text.

        Args:
            request: WorkflowRequest

        Returns:
            Parsed requirements
        """
        # Simple parsing - in production, this would use NLP
        requirements = {
            "topic": self._extract_topic(request.request_text),
            "content_types": [ct.value for ct in request.content_types],
            "priority": request.priority,
            "deadline": request.deadline,
            "additional_context": request.additional_context
        }

        return requirements

    def _extract_topic(self, request_text: str) -> str:
        """
        Extract topic from request text.

        Args:
            request_text: User's request

        Returns:
            Extracted topic
        """
        # Simple implementation - just return the request text
        # In production, this would use NLP to extract the actual topic
        return request_text

    def _create_execution_plan(self, workflow_type: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create step-by-step execution plan.

        Args:
            workflow_type: Type of workflow to execute
            requirements: Parsed requirements

        Returns:
            List of execution steps
        """
        workflow = self.workflows[workflow_type]
        sequence = workflow["sequence"]

        execution_plan = []
        for step_name in sequence:
            step = self._create_step(step_name, requirements)
            execution_plan.append(step)

        return execution_plan

    def _create_step(self, step_name: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single workflow step.

        Args:
            step_name: Name of the step
            requirements: Workflow requirements

        Returns:
            Step definition
        """
        step_definitions = {
            "research": {
                "agent": "research",
                "input": {"topic": requirements["topic"]},
                "output": "ResearchBrief",
                "quality_gate": "research_completeness"
            },
            "content_brief": {
                "skill": "content-brief",
                "input": "ResearchBrief",
                "output": "ContentBrief",
                "quality_gate": "brief_alignment"
            },
            "creation": {
                "agent": "creation",
                "input": "ContentBrief",
                "output": "DraftContent",
                "quality_gate": None
            },
            "creation_parallel": {
                "agent": "creation",
                "input": "ContentBrief",
                "output": "List[DraftContent]",
                "quality_gate": None,
                "parallel": True,
                "tracks": requirements.get("content_types", [])
            },
            "brand_voice": {
                "skill": "brand-voice",
                "input": "DraftContent",
                "output": "BrandVoiceResult",
                "quality_gate": "brand_consistency"
            },
            "production": {
                "agent": "production",
                "input": "DraftContent",
                "output": "ProductionOutput",
                "quality_gate": "format_compliance"
            }
        }

        return step_definitions.get(step_name, {"error": f"Unknown step: {step_name}"})

    def get_available_workflows(self) -> Dict[str, str]:
        """
        Get list of available workflows.

        Returns:
            Dictionary of workflow types and descriptions
        """
        return {
            wf_type: wf_def["description"]
            for wf_type, wf_def in self.workflows.items()
        }
