"""
Base Agent class for the Content Creation Engine.

All specialized agents (Orchestrator, Research, Creation, Production)
inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging


class Agent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize an agent.

        Args:
            name: Agent identifier
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Main processing method for the agent.

        Args:
            input_data: Input data for processing

        Returns:
            Processed output data
        """
        pass

    def log_execution(self, input_data: Any, output_data: Any, metadata: Optional[Dict[str, Any]] = None):
        """
        Log execution for debugging and monitoring.

        Args:
            input_data: Input that was processed
            output_data: Output that was generated
            metadata: Additional execution metadata
        """
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "input_type": type(input_data).__name__,
            "output_type": type(output_data).__name__,
            "metadata": metadata or {}
        }
        self.execution_history.append(execution_record)
        self.logger.info(f"Execution logged: {execution_record}")

    def validate_input(self, input_data: Any) -> tuple[bool, List[str]]:
        """
        Validate input data before processing.

        Args:
            input_data: Input to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Default implementation - override in subclasses
        if hasattr(input_data, 'validate'):
            return input_data.validate()
        return True, []

    def validate_output(self, output_data: Any) -> tuple[bool, List[str]]:
        """
        Validate output data after processing.

        Args:
            output_data: Output to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Default implementation - override in subclasses
        if hasattr(output_data, 'validate'):
            return output_data.validate()
        return True, []

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of agent executions.

        Returns:
            Summary statistics
        """
        return {
            "agent_name": self.name,
            "total_executions": len(self.execution_history),
            "first_execution": self.execution_history[0]["timestamp"] if self.execution_history else None,
            "last_execution": self.execution_history[-1]["timestamp"] if self.execution_history else None
        }


class Skill(ABC):
    """Base class for all skills in the system."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a skill.

        Args:
            name: Skill identifier
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"skill.{name}")

    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Execute the skill.

        Args:
            input_data: Input data for the skill
            **kwargs: Additional parameters

        Returns:
            Skill execution result
        """
        pass

    def validate_requirements(self) -> tuple[bool, List[str]]:
        """
        Validate that skill requirements are met.

        Returns:
            Tuple of (requirements_met, missing_requirements)
        """
        # Override in subclasses to check dependencies
        return True, []
