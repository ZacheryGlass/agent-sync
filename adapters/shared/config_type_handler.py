"""
Base interface for config type handlers.

Handlers encapsulate the logic for converting a specific config type
(AGENT, PERMISSION, PROMPT) between a format and canonical representation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from core.canonical_models import ConfigType


class ConfigTypeHandler(ABC):
    """
    Abstract base class for config type handlers.

    Each handler knows how to convert ONE config type (e.g., AGENT)
    for ONE format (e.g., Claude) to/from canonical representation.

    This enables separation of concerns where each handler focuses
    on a single config type's conversion logic, making the codebase
    more maintainable and scalable.

    Example:
        class ClaudeAgentHandler(ConfigTypeHandler):
            @property
            def config_type(self) -> ConfigType:
                return ConfigType.AGENT

            def to_canonical(self, content: str) -> CanonicalAgent:
                # Parse Claude agent format
                ...

            def from_canonical(self, canonical_obj: Any, options=None) -> str:
                # Generate Claude agent format
                ...
    """

    @property
    @abstractmethod
    def config_type(self) -> ConfigType:
        """
        The config type this handler processes.

        Returns:
            ConfigType enum value (AGENT, PERMISSION, PROMPT, etc.)
        """
        pass

    @abstractmethod
    def to_canonical(self, content: str) -> Any:
        """
        Convert format-specific content to canonical representation.

        Args:
            content: Raw content string from file

        Returns:
            Canonical object (CanonicalAgent, CanonicalPermission, etc.)

        Raises:
            ValueError: If content is invalid or malformed
        """
        pass

    @abstractmethod
    def from_canonical(self, canonical_obj: Any,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert canonical representation to format-specific content.

        Args:
            canonical_obj: Canonical object to convert
            options: Optional conversion options (format-specific)

        Returns:
            String content ready to write to file

        Raises:
            ValueError: If canonical_obj is wrong type or invalid
        """
        pass

    def get_warnings(self) -> list:
        """
        Return any conversion warnings generated.

        Override this method if your handler tracks warnings during conversion.

        Returns:
            List of warning messages (empty by default)
        """
        return []
