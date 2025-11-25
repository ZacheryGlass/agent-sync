"""
Format registry for managing available format adapters.

The registry acts as a central directory of all format adapters, providing:
- Adapter registration and lookup
- Auto-detection of format from file paths
- Validation of format support for config types
- Discovery of available formats

This enables plugin-style architecture where adapters can be dynamically
registered without modifying core code.
"""

from typing import Dict, List, Optional
from pathlib import Path
from .adapter_interface import FormatAdapter
from .canonical_models import ConfigType


class FormatRegistry:
    """
    Central registry for all format adapters.

    Usage:
        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        adapter = registry.get_adapter('claude')
        adapter = registry.detect_format(Path('agent.md'))
    """

    def __init__(self):
        """Initialize empty registry."""
        self._adapters: Dict[str, FormatAdapter] = {}

    def register(self, adapter: FormatAdapter):
        """
        Register a new format adapter.

        Args:
            adapter: FormatAdapter instance to register

        Raises:
            ValueError: If adapter with same format_name already registered

        Example:
            registry.register(ClaudeAdapter())
            registry.register(CopilotAdapter())
        """
        if adapter.format_name in self._adapters:
            raise ValueError(f"Adapter for format '{adapter.format_name}' already registered")
        self._adapters[adapter.format_name] = adapter

    def unregister(self, format_name: str):
        """
        Unregister a format adapter.

        Args:
            format_name: Name of format to unregister
        """
        if format_name in self._adapters:
            del self._adapters[format_name]

    def get_adapter(self, format_name: str) -> Optional[FormatAdapter]:
        """
        Get adapter by format name.

        Args:
            format_name: Format identifier (e.g., 'claude', 'copilot')

        Returns:
            FormatAdapter instance or None if not found
        """
        return self._adapters.get(format_name)

    def detect_format(self, file_path: Path) -> Optional[FormatAdapter]:
        """
        Auto-detect format from file path.

        Iterates through registered adapters and returns the first one
        whose can_handle() method returns True.

        Args:
            file_path: Path to file to detect format for

        Returns:
            FormatAdapter that can handle this file, or None if no match

        Example:
            adapter = registry.detect_format(Path('~/.claude/agents/planner.md'))
            # Returns ClaudeAdapter instance
        """
        for adapter in self._adapters.values():
            if adapter.can_handle(file_path):
                return adapter
        return None

    def list_formats(self) -> List[str]:
        """
        List all registered format names.

        Returns:
            List of format identifiers

        Example:
            formats = registry.list_formats()
            # ['claude', 'copilot', 'cursor']
        """
        return list(self._adapters.keys())

    def supports_config_type(self, format_name: str, config_type: ConfigType) -> bool:
        """
        Check if format supports a specific config type.

        Args:
            format_name: Format identifier
            config_type: ConfigType to check

        Returns:
            True if format supports this config type

        Example:
            registry.supports_config_type('claude', ConfigType.AGENT)  # True
            registry.supports_config_type('copilot', ConfigType.PERMISSION)  # False
        """
        adapter = self.get_adapter(format_name)
        return adapter and config_type in adapter.supported_config_types

    def get_formats_supporting(self, config_type: ConfigType) -> List[str]:
        """
        Get all formats that support a specific config type.

        Args:
            config_type: ConfigType to filter by

        Returns:
            List of format names that support this config type

        Example:
            formats = registry.get_formats_supporting(ConfigType.AGENT)
            # ['claude', 'copilot', 'cursor', 'windsurf']
        """
        return [
            format_name
            for format_name, adapter in self._adapters.items()
            if config_type in adapter.supported_config_types
        ]
