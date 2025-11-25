"""
Unit tests for format registry.

Tests cover:
- Adapter registration
- Adapter lookup
- Format detection
- Config type support queries

Status: STUB - To be implemented
"""

import pytest
from pathlib import Path

from core.registry import FormatRegistry
from core.canonical_models import ConfigType
from adapters import ClaudeAdapter, CopilotAdapter


class TestFormatRegistry:
    """Tests for FormatRegistry."""

    @pytest.fixture
    def registry(self):
        """Create FormatRegistry with some adapters."""
        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())
        return registry

    def test_register_adapter(self):
        """Test registering an adapter."""
        # TODO: Implement
        # registry = FormatRegistry()
        # adapter = ClaudeAdapter()
        # registry.register(adapter)
        # assert 'claude' in registry.list_formats()
        pass

    def test_register_duplicate_raises_error(self, registry):
        """Test that registering duplicate format raises error."""
        # TODO: Implement
        # with pytest.raises(ValueError):
        #     registry.register(ClaudeAdapter())
        pass

    def test_get_adapter(self, registry):
        """Test retrieving adapter by name."""
        # TODO: Implement
        # adapter = registry.get_adapter('claude')
        # assert adapter is not None
        # assert adapter.format_name == 'claude'
        pass

    def test_get_nonexistent_adapter(self, registry):
        """Test retrieving non-existent adapter returns None."""
        # TODO: Implement
        # assert registry.get_adapter('nonexistent') is None
        pass

    def test_detect_format(self, registry):
        """Test auto-detecting format from file path."""
        # TODO: Implement
        # adapter = registry.detect_format(Path('agent.md'))
        # assert adapter.format_name == 'claude'
        #
        # adapter = registry.detect_format(Path('agent.agent.md'))
        # assert adapter.format_name == 'copilot'
        pass

    def test_list_formats(self, registry):
        """Test listing all registered formats."""
        # TODO: Implement
        # formats = registry.list_formats()
        # assert 'claude' in formats
        # assert 'copilot' in formats
        pass

    def test_supports_config_type(self, registry):
        """Test checking if format supports config type."""
        # TODO: Implement
        # assert registry.supports_config_type('claude', ConfigType.AGENT)
        # assert not registry.supports_config_type('copilot', ConfigType.PERMISSION)
        pass

    def test_get_formats_supporting(self, registry):
        """Test getting all formats supporting a config type."""
        # TODO: Implement
        # formats = registry.get_formats_supporting(ConfigType.AGENT)
        # assert 'claude' in formats
        # assert 'copilot' in formats
        pass
