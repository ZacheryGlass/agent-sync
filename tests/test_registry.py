"""
Unit tests for format registry.

Tests cover:
- Adapter registration and unregistration
- Adapter lookup
- Format detection from file paths
- Config type support queries
- Error handling for edge cases
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
        registry = FormatRegistry()
        adapter = ClaudeAdapter()
        registry.register(adapter)
        assert 'claude' in registry.list_formats()
        assert registry.get_adapter('claude') is not None

    def test_register_duplicate_raises_error(self, registry):
        """Test that registering duplicate format raises error."""
        with pytest.raises(ValueError, match="already registered"):
            registry.register(ClaudeAdapter())

    def test_get_adapter(self, registry):
        """Test retrieving adapter by name."""
        adapter = registry.get_adapter('claude')
        assert adapter is not None
        assert adapter.format_name == 'claude'

        adapter = registry.get_adapter('copilot')
        assert adapter is not None
        assert adapter.format_name == 'copilot'

    def test_get_nonexistent_adapter(self, registry):
        """Test retrieving non-existent adapter returns None."""
        assert registry.get_adapter('nonexistent') is None
        assert registry.get_adapter('unknown-format') is None

    def test_detect_format(self, registry):
        """Test auto-detecting format from file path."""
        # Claude agent - plain .md file
        adapter = registry.detect_format(Path('agent.md'))
        assert adapter is not None
        assert adapter.format_name == 'claude'

        adapter = registry.detect_format(Path('~/.claude/agents/planner.md'))
        assert adapter is not None
        assert adapter.format_name == 'claude'

        # Copilot agent - .agent.md file
        adapter = registry.detect_format(Path('agent.agent.md'))
        assert adapter is not None
        assert adapter.format_name == 'copilot'

        adapter = registry.detect_format(Path('.github/agents/reviewer.agent.md'))
        assert adapter is not None
        assert adapter.format_name == 'copilot'

    def test_detect_format_no_match(self, registry):
        """Test that detecting unknown format returns None."""
        # File extensions that don't match any adapter
        assert registry.detect_format(Path('file.txt')) is None
        assert registry.detect_format(Path('script.py')) is None
        assert registry.detect_format(Path('config.json')) is None

    def test_list_formats(self, registry):
        """Test listing all registered formats."""
        formats = registry.list_formats()
        assert 'claude' in formats
        assert 'copilot' in formats
        assert len(formats) == 2

    def test_list_formats_empty(self):
        """Test listing formats for empty registry."""
        registry = FormatRegistry()
        assert registry.list_formats() == []

    def test_supports_config_type(self, registry):
        """Test checking if format supports config type."""
        # Both support AGENT config type
        assert registry.supports_config_type('claude', ConfigType.AGENT)
        assert registry.supports_config_type('copilot', ConfigType.AGENT)

        # Both support PERMISSION
        assert registry.supports_config_type('claude', ConfigType.PERMISSION)
        assert registry.supports_config_type('copilot', ConfigType.PERMISSION)

        # Claude supports SLASH_COMMAND, Copilot doesn't (yet)
        assert registry.supports_config_type('claude', ConfigType.SLASH_COMMAND)
        assert not registry.supports_config_type('copilot', ConfigType.SLASH_COMMAND)

    def test_supports_config_type_nonexistent(self, registry):
        """Test checking support for non-existent format returns False."""
        assert not registry.supports_config_type('unknown', ConfigType.AGENT)
        assert not registry.supports_config_type('nonexistent', ConfigType.PERMISSION)

    def test_get_formats_supporting(self, registry):
        """Test getting all formats supporting a config type."""
        # Both adapters support AGENT
        formats = registry.get_formats_supporting(ConfigType.AGENT)
        assert 'claude' in formats
        assert 'copilot' in formats
        assert len(formats) == 2

        # Both support PERMISSION
        formats = registry.get_formats_supporting(ConfigType.PERMISSION)
        assert 'claude' in formats
        assert 'copilot' in formats
        assert len(formats) == 2

        # Claude supports SLASH_COMMAND
        formats = registry.get_formats_supporting(ConfigType.SLASH_COMMAND)
        assert 'claude' in formats
        assert len(formats) == 1  # Only Claude for now (Copilot support TBD)

    def test_unregister_adapter(self, registry):
        """Test unregistering an adapter."""
        # Verify claude is registered
        assert 'claude' in registry.list_formats()
        assert registry.get_adapter('claude') is not None

        # Unregister it
        registry.unregister('claude')

        # Verify it's gone
        assert 'claude' not in registry.list_formats()
        assert registry.get_adapter('claude') is None

        # copilot should still be there
        assert 'copilot' in registry.list_formats()

    def test_unregister_nonexistent(self, registry):
        """Test unregistering non-existent format doesn't raise error."""
        # Should not raise any exception
        registry.unregister('nonexistent')
        registry.unregister('unknown-format')

        # Existing formats should still be there
        assert 'claude' in registry.list_formats()
        assert 'copilot' in registry.list_formats()
