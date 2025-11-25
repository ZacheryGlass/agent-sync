"""
Unit tests for format adapters.

Tests cover:
- ClaudeAdapter conversion (to/from canonical)
- CopilotAdapter conversion (to/from canonical)
- Round-trip conversions (Claude -> Canonical -> Claude)
- Field mapping and preservation
- Model name normalization
- Warning generation

Status: STUB - To be implemented
"""

import pytest
from pathlib import Path

from core.canonical_models import CanonicalAgent, ConfigType
from adapters import ClaudeAdapter, CopilotAdapter


class TestClaudeAdapter:
    """Tests for ClaudeAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create ClaudeAdapter instance."""
        return ClaudeAdapter()

    @pytest.fixture
    def sample_claude_content(self):
        """Sample Claude agent file content."""
        return """---
name: test-agent
description: Test agent description
tools: Read, Grep, Glob
model: sonnet
permissionMode: ask
---
Test agent instructions here.
"""

    def test_format_properties(self, adapter):
        """Test adapter properties."""
        # TODO: Implement
        # assert adapter.format_name == "claude"
        # assert adapter.file_extension == ".md"
        # assert ConfigType.AGENT in adapter.supported_config_types
        pass

    def test_can_handle(self, adapter):
        """Test file detection."""
        # TODO: Implement
        # assert adapter.can_handle(Path("agent.md")) == True
        # assert adapter.can_handle(Path("agent.agent.md")) == False
        pass

    def test_to_canonical(self, adapter, sample_claude_content):
        """Test conversion from Claude format to canonical."""
        # TODO: Implement
        # agent = adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        # assert agent.name == "test-agent"
        # assert agent.description == "Test agent description"
        # assert agent.tools == ["Read", "Grep", "Glob"]
        # assert agent.model == "sonnet"
        # assert agent.get_metadata('claude_permission_mode') == 'ask'
        pass

    def test_from_canonical(self, adapter):
        """Test conversion from canonical to Claude format."""
        # TODO: Implement
        pass

    def test_round_trip(self, adapter, sample_claude_content):
        """Test Claude -> Canonical -> Claude preserves data."""
        # TODO: Implement
        # canonical = adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        # output = adapter.from_canonical(canonical, ConfigType.AGENT)
        # canonical2 = adapter.to_canonical(output, ConfigType.AGENT)
        # assert canonical.name == canonical2.name
        # assert canonical.get_metadata('claude_permission_mode') == canonical2.get_metadata('claude_permission_mode')
        pass


class TestCopilotAdapter:
    """Tests for CopilotAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create CopilotAdapter instance."""
        return CopilotAdapter()

    @pytest.fixture
    def sample_copilot_content(self):
        """Sample Copilot agent file content."""
        return """---
name: test-agent
description: Test agent description
tools: [read, grep, glob]
model: Claude Sonnet 4
target: vscode
---
Test agent instructions here.
"""

    def test_format_properties(self, adapter):
        """Test adapter properties."""
        # TODO: Implement
        pass

    def test_can_handle(self, adapter):
        """Test file detection."""
        # TODO: Implement
        # assert adapter.can_handle(Path("agent.agent.md")) == True
        # assert adapter.can_handle(Path("agent.md")) == False
        pass

    def test_to_canonical(self, adapter, sample_copilot_content):
        """Test conversion from Copilot format to canonical."""
        # TODO: Implement
        pass

    def test_from_canonical(self, adapter):
        """Test conversion from canonical to Copilot format."""
        # TODO: Implement
        pass

    def test_model_name_mapping(self, adapter):
        """Test model name conversion."""
        # TODO: Implement
        # assert adapter._normalize_model("Claude Sonnet 4") == "sonnet"
        # assert adapter._denormalize_model("sonnet") == "Claude Sonnet 4"
        pass


class TestCrossFormatConversion:
    """Tests for converting between different formats."""

    def test_claude_to_copilot(self):
        """Test Claude -> Canonical -> Copilot conversion."""
        # TODO: Implement
        pass

    def test_copilot_to_claude(self):
        """Test Copilot -> Canonical -> Claude conversion."""
        # TODO: Implement
        pass

    def test_metadata_preservation(self):
        """Test that format-specific metadata is preserved."""
        # TODO: Implement
        # Claude -> Copilot -> Claude should preserve permissionMode
        pass
