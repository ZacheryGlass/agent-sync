"""
Unit tests for canonical data models.

Tests cover:
- CanonicalAgent creation and manipulation
- CanonicalPermission creation
- CanonicalPrompt creation
- Metadata handling
- ConfigType enum

Status: STUB - To be implemented
"""

import pytest
from core.canonical_models import CanonicalAgent, CanonicalPermission, CanonicalPrompt, ConfigType


class TestCanonicalAgent:
    """Tests for CanonicalAgent model."""

    def test_create_minimal_agent(self):
        """Test creating agent with minimal required fields."""
        # TODO: Implement
        pass

    def test_create_full_agent(self):
        """Test creating agent with all fields."""
        # TODO: Implement
        pass

    def test_metadata_operations(self):
        """Test adding, getting, and checking metadata."""
        # TODO: Implement
        # agent.add_metadata('key', 'value')
        # assert agent.get_metadata('key') == 'value'
        # assert agent.has_metadata('key')
        pass

    def test_tools_list(self):
        """Test tools list handling."""
        # TODO: Implement
        pass


class TestCanonicalPermission:
    """Tests for CanonicalPermission model."""

    def test_create_permission(self):
        """Test creating permission configuration."""
        # TODO: Implement
        pass


class TestCanonicalPrompt:
    """Tests for CanonicalPrompt model."""

    def test_create_prompt(self):
        """Test creating saved prompt."""
        # TODO: Implement
        pass


class TestConfigType:
    """Tests for ConfigType enum."""

    def test_enum_values(self):
        """Test ConfigType enum has expected values."""
        # TODO: Implement
        # assert ConfigType.AGENT.value == "agent"
        # assert ConfigType.PERMISSION.value == "permission"
        # assert ConfigType.PROMPT.value == "prompt"
        pass
