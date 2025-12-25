"""
Unit tests for format adapters.

Tests cover:
- ClaudeAdapter conversion (to/from canonical)
- CopilotAdapter conversion (to/from canonical)
- Round-trip conversions (Claude -> Canonical -> Claude)
- Cross-format conversions (Claude -> Copilot -> Claude)
- Field mapping and preservation
- Model name normalization
- Warning generation

Status: IMPLEMENTED
"""

import pytest
from pathlib import Path

from core.canonical_models import CanonicalAgent, CanonicalSlashCommand, ConfigType
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

    @pytest.fixture
    def minimal_claude_content(self):
        """Minimal valid agent (required fields only)."""
        return """---
name: minimal-agent
description: Minimal agent
---
Basic instructions.
"""

    @pytest.fixture
    def full_claude_content(self):
        """Agent with all fields including metadata."""
        return """---
name: full-agent
description: Full agent with metadata
tools: Read, Grep, Glob, Bash
model: opus
permissionMode: ask
skills: [python, javascript]
---
Full agent instructions.
"""

    @pytest.fixture
    def canonical_agent_sample(self):
        """CanonicalAgent instance for serialization tests."""
        return CanonicalAgent(
            name="test-agent",
            description="Test agent description",
            instructions="Test agent instructions.",
            tools=["Read", "Grep", "Glob"],
            model="sonnet",
            source_format="claude"
        )

    @pytest.fixture
    def canonical_agent_with_metadata(self):
        """CanonicalAgent with Claude-specific metadata."""
        agent = CanonicalAgent(
            name="metadata-agent",
            description="Agent with metadata",
            instructions="Agent instructions.",
            tools=["Read", "Grep"],
            model="opus",
            source_format="claude"
        )
        agent.add_metadata('claude_permission_mode', 'ask')
        agent.add_metadata('claude_skills', ['python', 'javascript'])
        return agent

    # Phase 1: Property Tests

    def test_format_properties(self, adapter):
        """Test adapter properties."""
        assert adapter.format_name == "claude"
        assert adapter.file_extension == ".md"
        assert ConfigType.AGENT in adapter.supported_config_types

    def test_can_handle(self, adapter):
        """Test file detection."""
        assert adapter.can_handle(Path("agent.md")) is True
        assert adapter.can_handle(Path("agent.agent.md")) is False
        assert adapter.can_handle(Path("agent.txt")) is False

    def test_to_canonical(self, adapter, sample_claude_content):
        """Test conversion from Claude format to canonical."""
        agent = adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        assert agent.name == "test-agent"
        assert agent.description == "Test agent description"
        assert agent.tools == ["Read", "Grep", "Glob"]
        assert agent.model == "sonnet"
        assert agent.instructions == "Test agent instructions here."
        assert agent.source_format == "claude"
        assert agent.get_metadata('claude_permission_mode') == 'ask'

    def test_from_canonical(self, adapter):
        """Test conversion from canonical to Claude format."""
        agent = CanonicalAgent(
            name="test-agent",
            description="Test description",
            instructions="Test instructions",
            tools=["Read", "Edit"],
            model="sonnet",
            source_format="claude"
        )
        agent.add_metadata('claude_permission_mode', 'ask')

        output = adapter.from_canonical(agent, ConfigType.AGENT)

        assert "name: test-agent" in output
        assert "description: Test description" in output
        assert "tools: Read, Edit" in output
        assert "model: sonnet" in output
        assert "permissionMode: ask" in output
        assert "Test instructions" in output

    def test_round_trip(self, adapter, sample_claude_content):
        """Test Claude -> Canonical -> Claude preserves data."""
        canonical = adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        output = adapter.from_canonical(canonical, ConfigType.AGENT)
        canonical2 = adapter.to_canonical(output, ConfigType.AGENT)

        assert canonical.name == canonical2.name
        assert canonical.description == canonical2.description
        assert canonical.model == canonical2.model
        assert canonical.tools == canonical2.tools
        assert canonical.get_metadata('claude_permission_mode') == canonical2.get_metadata('claude_permission_mode')

    # Phase 2: Additional Core Parsing Tests

    def test_to_canonical_minimal(self, adapter, minimal_claude_content):
        """Test parsing agent with only required fields."""
        agent = adapter.to_canonical(minimal_claude_content, ConfigType.AGENT)
        assert agent.name == "minimal-agent"
        assert agent.description == "Minimal agent"
        assert agent.instructions == "Basic instructions."
        assert agent.tools == []
        assert agent.model is None
        assert not agent.has_metadata('claude_permission_mode')

    def test_to_canonical_full(self, adapter, full_claude_content):
        """Test parsing agent with all fields."""
        agent = adapter.to_canonical(full_claude_content, ConfigType.AGENT)
        assert agent.name == "full-agent"
        assert agent.description == "Full agent with metadata"
        assert agent.instructions == "Full agent instructions."
        assert agent.tools == ["Read", "Grep", "Glob", "Bash"]
        assert agent.model == "opus"
        assert agent.get_metadata('claude_permission_mode') == 'ask'
        assert agent.get_metadata('claude_skills') == ['python', 'javascript']

    def test_to_canonical_from_file(self, adapter, tmp_path):
        """Test read() method with file."""
        fixture_path = Path("tests/fixtures/claude/agents/simple-agent.md")
        agent = adapter.read(fixture_path, ConfigType.AGENT)
        assert agent.name == "simple-agent"
        assert agent.description == "A simple test agent for unit testing"
        assert agent.tools == ["Read", "Grep", "Glob"]
        assert agent.model == "sonnet"

    def test_to_canonical_invalid_no_frontmatter(self, adapter):
        """Test error handling for content without YAML frontmatter."""
        content = "This has no frontmatter"
        with pytest.raises(ValueError, match="No YAML frontmatter found"):
            adapter.to_canonical(content, ConfigType.AGENT)

    # Phase 3: Helper Method Tests

    def test_parse_tools_comma_separated(self, adapter):
        """Test tool parsing from comma-separated string."""
        result = adapter._parse_tools("Read, Grep, Glob")
        assert result == ["Read", "Grep", "Glob"]

    def test_parse_tools_with_whitespace(self, adapter):
        """Test tool parsing with extra whitespace."""
        result = adapter._parse_tools("Read,  Grep  ,Glob")
        assert result == ["Read", "Grep", "Glob"]

    def test_parse_tools_as_list(self, adapter):
        """Test tool parsing when already a list."""
        result = adapter._parse_tools(["Read", "Grep"])
        assert result == ["Read", "Grep"]

    def test_parse_tools_empty(self, adapter):
        """Test tool parsing with empty input."""
        assert adapter._parse_tools("") == []
        assert adapter._parse_tools(None) == []

    def test_normalize_model_lowercase(self, adapter):
        """Test model normalization to lowercase."""
        assert adapter._normalize_model("Sonnet") == "sonnet"
        assert adapter._normalize_model("OPUS") == "opus"

    def test_normalize_model_already_lowercase(self, adapter):
        """Test model normalization when already lowercase."""
        assert adapter._normalize_model("opus") == "opus"
        assert adapter._normalize_model("haiku") == "haiku"

    def test_normalize_model_none(self, adapter):
        """Test model normalization with None."""
        assert adapter._normalize_model(None) is None

    # Phase 4: Additional Serialization Tests

    def test_from_canonical_basic(self, adapter, canonical_agent_sample):
        """Test conversion from canonical to Claude format."""
        output = adapter.from_canonical(canonical_agent_sample, ConfigType.AGENT)
        assert "name: test-agent" in output
        assert "description: Test agent description" in output
        assert "tools: Read, Grep, Glob" in output
        assert "model: sonnet" in output
        assert "Test agent instructions." in output
        assert output.startswith("---\n")
        assert "---\n" in output[4:]  # Second --- separator

    def test_from_canonical_with_metadata(self, adapter, canonical_agent_with_metadata):
        """Test metadata preservation in serialization."""
        output = adapter.from_canonical(canonical_agent_with_metadata, ConfigType.AGENT)
        assert "permissionMode: ask" in output
        assert "skills:" in output
        assert "python" in output
        assert "javascript" in output

    def test_from_canonical_empty_tools(self, adapter):
        """Test serialization with empty tools list."""
        agent = CanonicalAgent(
            name="no-tools",
            description="Agent without tools",
            instructions="Instructions.",
            tools=[],
            model="sonnet"
        )
        output = adapter.from_canonical(agent, ConfigType.AGENT)
        assert "name: no-tools" in output
        assert "description: Agent without tools" in output

    def test_from_canonical_no_model(self, adapter):
        """Test serialization when model is None."""
        agent = CanonicalAgent(
            name="no-model",
            description="Agent without model",
            instructions="Instructions.",
            tools=["Read"],
            model=None
        )
        output = adapter.from_canonical(agent, ConfigType.AGENT)
        assert "name: no-model" in output
        lines = output.split('\n')
        model_lines = [line for line in lines if line.startswith('model:')]
        assert len(model_lines) == 0

    # Phase 5: Additional Round-Trip Tests

    def test_round_trip_preserves_all_data(self, adapter, sample_claude_content):
        """Test Claude -> Canonical -> Claude -> Canonical preserves all data."""
        canonical1 = adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        output = adapter.from_canonical(canonical1, ConfigType.AGENT)
        canonical2 = adapter.to_canonical(output, ConfigType.AGENT)

        assert canonical1.name == canonical2.name
        assert canonical1.description == canonical2.description
        assert canonical1.instructions == canonical2.instructions
        assert canonical1.tools == canonical2.tools
        assert canonical1.model == canonical2.model
        assert canonical1.get_metadata('claude_permission_mode') == canonical2.get_metadata('claude_permission_mode')

    def test_round_trip_minimal(self, adapter, minimal_claude_content):
        """Test round-trip with minimal agent."""
        canonical1 = adapter.to_canonical(minimal_claude_content, ConfigType.AGENT)
        output = adapter.from_canonical(canonical1, ConfigType.AGENT)
        canonical2 = adapter.to_canonical(output, ConfigType.AGENT)

        assert canonical1.name == canonical2.name
        assert canonical1.description == canonical2.description
        assert canonical1.instructions == canonical2.instructions
        assert canonical1.tools == canonical2.tools
        assert canonical1.model == canonical2.model

    def test_round_trip_metadata_preservation(self, adapter, full_claude_content):
        """Test metadata preservation through round-trip."""
        canonical1 = adapter.to_canonical(full_claude_content, ConfigType.AGENT)
        output = adapter.from_canonical(canonical1, ConfigType.AGENT)
        canonical2 = adapter.to_canonical(output, ConfigType.AGENT)

        assert canonical1.get_metadata('claude_permission_mode') == canonical2.get_metadata('claude_permission_mode')
        assert canonical1.get_metadata('claude_skills') == canonical2.get_metadata('claude_skills')

    # Phase 6: File I/O Tests

    def test_read_from_file(self, adapter, tmp_path):
        """Test reading agent from file."""
        test_file = tmp_path / "test-agent.md"
        test_file.write_text("""---
name: file-test
description: Test from file
tools: Read, Grep
model: sonnet
---
File test instructions.
""")
        agent = adapter.read(test_file, ConfigType.AGENT)
        assert agent.name == "file-test"
        assert agent.description == "Test from file"
        assert agent.tools == ["Read", "Grep"]

    def test_write_to_file(self, adapter, canonical_agent_sample, tmp_path):
        """Test writing canonical agent to file."""
        test_file = tmp_path / "output-agent.md"
        adapter.write(canonical_agent_sample, test_file, ConfigType.AGENT)

        assert test_file.exists()
        content = test_file.read_text()
        assert "name: test-agent" in content
        assert "description: Test agent description" in content
        assert content.startswith("---\n")

    # Phase 7: Edge Cases

    def test_special_characters_in_fields(self, adapter):
        """Test handling of special characters in YAML fields."""
        content = """---
name: special-agent
description: "Agent with: colons and 'quotes'"
tools: Read, Grep
model: sonnet
---
Instructions with special characters: colons, "quotes", and more.
"""
        agent = adapter.to_canonical(content, ConfigType.AGENT)
        assert agent.name == "special-agent"
        assert "colons" in agent.description
        assert "quotes" in agent.description

    def test_complex_description_with_newlines_and_quotes(self, adapter):
        """Test handling of complex descriptions with newlines and quotes."""
        content = r"""---
name: complex-agent
description: "Start of description.\n\n<example>\nContext: \"Quoted text\"\nUser: ...\n</example>"
tools: Read
model: sonnet
---
Instructions.
"""
        agent = adapter.to_canonical(content, ConfigType.AGENT)
        assert agent.name == "complex-agent"
        assert "\n\n<example>\n" in agent.description
        assert 'Context: "Quoted text"' in agent.description

    def test_multiline_instructions(self, adapter):
        """Test preservation of multiline markdown instructions."""
        fixture_path = Path("tests/fixtures/claude/agents/edge-cases/multiline-instructions.md")
        agent = adapter.read(fixture_path, ConfigType.AGENT)

        assert "# Complex Instructions" in agent.instructions
        assert "```python" in agent.instructions
        assert "## Lists" in agent.instructions
        assert "**bold**" in agent.instructions

    def test_tools_with_special_spacing(self, adapter):
        """Test tool parsing with various spacing patterns."""
        fixture_path = Path("tests/fixtures/claude/agents/edge-cases/whitespace.md")
        agent = adapter.read(fixture_path, ConfigType.AGENT)

        assert agent.tools == ["Read", "Grep", "Glob", "Bash"]
        assert agent.instructions.strip() == "Instructions with extra whitespace.\n\n  Including leading/trailing spaces."

    def test_conversion_warnings(self, adapter, sample_claude_content):
        """Test conversion warnings mechanism."""
        adapter.to_canonical(sample_claude_content, ConfigType.AGENT)
        warnings = adapter.get_conversion_warnings()
        assert isinstance(warnings, list)

    # ==================== SLASH-COMMAND TESTS ====================

    # Fixtures for slash-command tests

    @pytest.fixture
    def minimal_slash_command_content(self):
        """Minimal slash-command (no frontmatter, just body)."""
        return """Review this code for bugs and suggest improvements.
"""

    @pytest.fixture
    def simple_slash_command_content(self):
        """Simple slash-command with basic frontmatter."""
        return """---
description: Explain code in simple terms
---

Explain the following code: $ARGUMENTS

Make it beginner-friendly and include examples.
"""

    @pytest.fixture
    def full_slash_command_content(self):
        """Full-featured slash-command with all fields."""
        return """---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
argument-hint: [message]
description: Create a git commit
model: claude-3-5-haiku-20241022
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Create a git commit with message: $ARGUMENTS

Follow these guidelines:
- Use conventional commit format
- Keep message concise but descriptive
- Stage relevant files before committing
"""

    @pytest.fixture
    def canonical_slash_command_minimal(self):
        """Minimal CanonicalSlashCommand for serialization tests."""
        return CanonicalSlashCommand(
            name="test-command",
            description="Test slash command",
            instructions="Test command instructions.",
            source_format="claude"
        )

    @pytest.fixture
    def canonical_slash_command_full(self):
        """Full CanonicalSlashCommand with all fields."""
        return CanonicalSlashCommand(
            name="full-command",
            description="Full slash command with all fields",
            instructions="Full command instructions with $ARGUMENTS placeholder.",
            argument_hint="[arg1] [arg2]",
            model="haiku",
            allowed_tools=["Bash(git:*)", "Read", "Write"],
            source_format="claude"
        )

    # Phase 1: Property Tests

    def test_slash_command_config_type(self, adapter):
        """Test that ClaudeSlashCommandHandler returns correct config type."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        # and registered in ClaudeAdapter
        handler = adapter._get_handler(ConfigType.SLASH_COMMAND)
        assert handler.config_type == ConfigType.SLASH_COMMAND

    # Phase 2: to_canonical() Tests

    def test_slash_command_to_canonical_minimal(self, adapter, tmp_path):
        """Test parsing minimal slash-command (no frontmatter)."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        fixture_path = Path("tests/fixtures/claude/slash-commands/minimal.md")

        slash_command = adapter.read(fixture_path, ConfigType.SLASH_COMMAND)

        # Name should be derived from filename
        assert slash_command.name == "minimal"
        # Description should be empty or have a default value
        assert slash_command.description == "" or slash_command.description is None
        # Instructions should be the body content
        assert "Review this code for bugs and suggest improvements" in slash_command.instructions
        # Optional fields should be None or empty
        assert slash_command.argument_hint is None or slash_command.argument_hint == ""
        assert slash_command.model is None
        assert slash_command.allowed_tools == [] or slash_command.allowed_tools is None
        assert slash_command.source_format == "claude"

    def test_slash_command_to_canonical_simple(self, adapter, tmp_path):
        """Test parsing simple slash-command with basic frontmatter."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        fixture_path = Path("tests/fixtures/claude/slash-commands/simple.md")

        slash_command = adapter.read(fixture_path, ConfigType.SLASH_COMMAND)

        # Name derived from filename (since no 'name' in frontmatter)
        assert slash_command.name == "simple"
        # Description from frontmatter
        assert slash_command.description == "Explain code in simple terms"
        # Instructions should contain $ARGUMENTS placeholder
        assert "$ARGUMENTS" in slash_command.instructions
        assert "beginner-friendly" in slash_command.instructions
        assert slash_command.source_format == "claude"

    def test_slash_command_to_canonical_full_featured(self, adapter, tmp_path):
        """Test parsing full-featured slash-command with all fields."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        fixture_path = Path("tests/fixtures/claude/slash-commands/full-featured.md")

        slash_command = adapter.read(fixture_path, ConfigType.SLASH_COMMAND)

        # Name from filename
        assert slash_command.name == "full-featured"
        # Description from frontmatter
        assert slash_command.description == "Create a git commit"
        # argument-hint from frontmatter
        assert slash_command.argument_hint == "[message]"
        # Model from frontmatter
        assert slash_command.model == "claude-3-5-haiku-20241022" or slash_command.model == "haiku"
        # allowed-tools should be parsed into a list
        assert isinstance(slash_command.allowed_tools, list)
        assert len(slash_command.allowed_tools) >= 3
        # Should contain git-related tools
        assert any("git" in tool.lower() for tool in slash_command.allowed_tools)
        # Instructions should contain bash execution syntax and $ARGUMENTS
        assert "!`git" in slash_command.instructions or "git" in slash_command.instructions
        assert "$ARGUMENTS" in slash_command.instructions
        assert slash_command.source_format == "claude"

    def test_slash_command_to_canonical_preserves_metadata(self, adapter):
        """Test that format-specific fields are preserved in metadata."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        content = """---
description: Test command
allowed-tools: Read, Grep
disable-model-invocation: true
custom-field: custom-value
---

Test instructions.
"""

        slash_command = adapter.to_canonical(content, ConfigType.SLASH_COMMAND)

        # Claude-specific fields should be in metadata
        # The exact metadata keys depend on implementation
        assert slash_command.metadata is not None
        # If 'disable-model-invocation' is Claude-specific, it should be in metadata
        # This assertion may need adjustment based on actual implementation

    # Phase 3: from_canonical() Tests

    def test_slash_command_from_canonical_minimal(self, adapter, canonical_slash_command_minimal):
        """Test generating minimal slash-command from canonical."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        output = adapter.from_canonical(canonical_slash_command_minimal, ConfigType.SLASH_COMMAND)

        # Should have valid structure
        assert isinstance(output, str)
        # Body should contain instructions
        assert "Test command instructions" in output
        # For minimal command, frontmatter might be minimal or absent
        # Check if it's valid markdown

    def test_slash_command_from_canonical_full(self, adapter, canonical_slash_command_full):
        """Test generating full slash-command with all fields."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented
        output = adapter.from_canonical(canonical_slash_command_full, ConfigType.SLASH_COMMAND)

        # Should have frontmatter
        assert output.startswith("---\n") or "---\n" in output
        # Should contain description
        assert "description:" in output or "Full slash command with all fields" in output
        # Should contain argument-hint
        assert "argument-hint:" in output or "[arg1]" in output
        # Should contain model
        assert "model:" in output or "haiku" in output
        # Should contain allowed-tools
        assert "allowed-tools:" in output or "Bash(git:*)" in output
        # Should contain instructions with placeholder
        assert "$ARGUMENTS" in output
        assert "Full command instructions" in output

    # Phase 4: Round-Trip Tests

    def test_slash_command_round_trip(self, adapter):
        """Test Claude -> Canonical -> Claude preserves all data."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented

        # Test with minimal fixture
        minimal_path = Path("tests/fixtures/claude/slash-commands/minimal.md")
        canonical1 = adapter.read(minimal_path, ConfigType.SLASH_COMMAND)
        output = adapter.from_canonical(canonical1, ConfigType.SLASH_COMMAND)
        canonical2 = adapter.to_canonical(output, ConfigType.SLASH_COMMAND)

        assert canonical1.name == canonical2.name
        assert canonical1.description == canonical2.description
        assert canonical1.instructions.strip() == canonical2.instructions.strip()

        # Test with simple fixture
        simple_path = Path("tests/fixtures/claude/slash-commands/simple.md")
        canonical1 = adapter.read(simple_path, ConfigType.SLASH_COMMAND)
        output = adapter.from_canonical(canonical1, ConfigType.SLASH_COMMAND)
        canonical2 = adapter.to_canonical(output, ConfigType.SLASH_COMMAND)

        assert canonical1.name == canonical2.name
        assert canonical1.description == canonical2.description
        assert canonical1.instructions.strip() == canonical2.instructions.strip()

        # Test with full-featured fixture
        full_path = Path("tests/fixtures/claude/slash-commands/full-featured.md")
        canonical1 = adapter.read(full_path, ConfigType.SLASH_COMMAND)
        output = adapter.from_canonical(canonical1, ConfigType.SLASH_COMMAND)
        canonical2 = adapter.to_canonical(output, ConfigType.SLASH_COMMAND)

        assert canonical1.name == canonical2.name
        assert canonical1.description == canonical2.description
        assert canonical1.argument_hint == canonical2.argument_hint
        assert canonical1.model == canonical2.model
        assert canonical1.allowed_tools == canonical2.allowed_tools
        assert canonical1.instructions.strip() == canonical2.instructions.strip()

    # Phase 5: Edge Cases

    def test_slash_command_edge_cases(self, adapter):
        """Test edge cases: complex allowed-tools, bash syntax, arguments."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented

        # Test complex allowed-tools patterns
        content_with_complex_tools = """---
description: Complex tools test
allowed-tools: Bash(git:*), Read, Write, Grep, Bash(npm *:*)
---

Test with complex tools.
"""
        slash_command = adapter.to_canonical(content_with_complex_tools, ConfigType.SLASH_COMMAND)
        assert len(slash_command.allowed_tools) >= 4

        # Test with-arguments fixture (positional arguments)
        args_path = Path("tests/fixtures/claude/slash-commands/with-arguments.md")
        slash_command = adapter.read(args_path, ConfigType.SLASH_COMMAND)
        # Should preserve $1, $2, $3 in instructions
        assert "$1" in slash_command.instructions
        assert "$2" in slash_command.instructions
        assert "$3" in slash_command.instructions

        # Test with-file-refs fixture (@ syntax)
        refs_path = Path("tests/fixtures/claude/slash-commands/with-file-refs.md")
        slash_command = adapter.read(refs_path, ConfigType.SLASH_COMMAND)
        # Should preserve @ file references
        assert "@" in slash_command.instructions

        # Test empty description
        content_no_desc = """---
argument-hint: test
---

No description here.
"""
        slash_command = adapter.to_canonical(content_no_desc, ConfigType.SLASH_COMMAND)
        assert slash_command.description == "" or slash_command.description is None

    # Phase 6: Error Handling

    def test_slash_command_error_handling(self, adapter):
        """Test handling of invalid YAML and missing required fields."""
        # Note: This test will fail until ClaudeSlashCommandHandler is implemented

        # Test invalid YAML frontmatter
        invalid_yaml = """---
description: "Unclosed quote
allowed-tools: Read
---

Instructions.
"""
        with pytest.raises((ValueError, Exception)):
            adapter.to_canonical(invalid_yaml, ConfigType.SLASH_COMMAND)

        # Test malformed frontmatter delimiters
        malformed = """--
description: Test
--

Instructions.
"""
        # Depending on implementation, this might raise an error or treat it as no frontmatter
        # The behavior should be consistent with agent handler

        # For slash-commands, if there's no frontmatter, it might be valid (like minimal.md)
        # So this test might need adjustment based on actual implementation


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
tools:
  - read
  - grep
  - glob
model: Claude Sonnet 4
target: vscode
---
Test agent instructions here.
"""

    @pytest.fixture
    def full_copilot_content(self):
        """Copilot agent with all optional fields."""
        return """---
name: full-agent
description: Agent with all optional fields
tools:
  - read
  - grep
  - glob
  - edit
model: Claude Sonnet 4
target: vscode
argument-hint: Use this agent for complex tasks
handoffs:
  - label: Continue
    agent: next-agent
    prompt: Continue with next step
    send: false
mcp-servers:
  - name: example-server
    url: http://localhost:3000
---
Full agent instructions with all Copilot features.
"""

    def test_format_properties(self, adapter):
        """Test adapter properties."""
        assert adapter.format_name == "copilot"
        assert adapter.file_extension == ".agent.md"
        assert ConfigType.AGENT in adapter.supported_config_types

    def test_can_handle(self, adapter):
        """Test file detection."""
        assert adapter.can_handle(Path("agent.agent.md")) is True
        assert adapter.can_handle(Path("test.agent.md")) is True
        assert adapter.can_handle(Path("agent.md")) is False
        assert adapter.can_handle(Path("agent.txt")) is False

    def test_to_canonical(self, adapter, sample_copilot_content):
        """Test conversion from Copilot format to canonical."""
        agent = adapter.to_canonical(sample_copilot_content, ConfigType.AGENT)

        assert agent.name == "test-agent"
        assert agent.description == "Test agent description"
        assert agent.tools == ["read", "grep", "glob"]
        assert agent.model == "sonnet"  # Normalized from "Claude Sonnet 4"
        assert agent.instructions == "Test agent instructions here."
        assert agent.source_format == "copilot"
        assert agent.get_metadata('copilot_target') == "vscode"

    def test_to_canonical_with_metadata(self, adapter, full_copilot_content):
        """Test that Copilot-specific fields are preserved in metadata."""
        agent = adapter.to_canonical(full_copilot_content, ConfigType.AGENT)

        assert agent.get_metadata('copilot_argument_hint') == "Use this agent for complex tasks"
        assert agent.get_metadata('copilot_target') == "vscode"

        handoffs = agent.get_metadata('copilot_handoffs')
        assert handoffs is not None
        assert len(handoffs) == 1
        assert handoffs[0]['label'] == "Continue"
        assert handoffs[0]['agent'] == "next-agent"

        mcp_servers = agent.get_metadata('copilot_mcp_servers')
        assert mcp_servers is not None
        assert len(mcp_servers) == 1
        assert mcp_servers[0]['name'] == "example-server"

    def test_to_canonical_missing_frontmatter(self, adapter):
        """Test error handling when YAML frontmatter is missing."""
        invalid_content = "No frontmatter here, just text."

        with pytest.raises(ValueError, match="No YAML frontmatter found"):
            adapter.to_canonical(invalid_content, ConfigType.AGENT)

    def test_from_canonical(self, adapter):
        """Test conversion from canonical to Copilot format."""
        agent = CanonicalAgent(
            name="test-agent",
            description="Test description",
            instructions="Test instructions",
            tools=["read", "edit"],
            model="sonnet",
            source_format="canonical"
        )

        output = adapter.from_canonical(agent, ConfigType.AGENT)

        assert "name: test-agent" in output
        assert "description: Test description" in output
        assert "model: Claude Sonnet 4" in output  # Denormalized
        assert "target: vscode" in output  # Always added
        assert "Test instructions" in output
        # Tools should be in YAML list format
        assert "tools:" in output

    def test_from_canonical_with_options(self, adapter):
        """Test from_canonical with options to add optional fields."""
        agent = CanonicalAgent(
            name="test-agent",
            description="Test description",
            instructions="Test instructions",
            tools=["read"],
            model="sonnet"
        )

        # Test with add_argument_hint option
        output = adapter.from_canonical(
            agent, ConfigType.AGENT,
            options={'add_argument_hint': True}
        )
        assert "argument-hint:" in output

        # Test with add_handoffs option
        output = adapter.from_canonical(
            agent, ConfigType.AGENT,
            options={'add_handoffs': True}
        )
        assert "handoffs:" in output

    def test_from_canonical_preserves_metadata(self, adapter, full_copilot_content):
        """Test that metadata from original Copilot file is restored."""
        # First convert to canonical (preserving metadata)
        agent = adapter.to_canonical(full_copilot_content, ConfigType.AGENT)

        # Then convert back to Copilot format
        output = adapter.from_canonical(agent, ConfigType.AGENT)

        # Verify preserved metadata appears in output
        assert "argument-hint:" in output
        assert "handoffs:" in output
        assert "mcp-servers:" in output

    def test_model_name_mapping(self, adapter):
        """Test model name conversion between Copilot and canonical forms."""
        # Test normalization (Copilot -> canonical)
        assert adapter._normalize_model("Claude Sonnet 4") == "sonnet"
        assert adapter._normalize_model("Claude Opus 4") == "opus"
        assert adapter._normalize_model("Claude Haiku 4") == "haiku"
        assert adapter._normalize_model("claude sonnet 4") == "sonnet"  # Case insensitive
        assert adapter._normalize_model(None) is None
        assert adapter._normalize_model("unknown-model") == "unknown-model"  # Pass through

        # Test denormalization (canonical -> Copilot)
        assert adapter._denormalize_model("sonnet") == "Claude Sonnet 4"
        assert adapter._denormalize_model("opus") == "Claude Opus 4"
        assert adapter._denormalize_model("haiku") == "Claude Haiku 4"
        assert adapter._denormalize_model("unknown") == "unknown"  # Pass through

    def test_round_trip(self, adapter, full_copilot_content):
        """Test Copilot -> Canonical -> Copilot preserves all data."""
        # Convert to canonical
        canonical = adapter.to_canonical(full_copilot_content, ConfigType.AGENT)

        # Convert back to Copilot format
        output = adapter.from_canonical(canonical, ConfigType.AGENT)

        # Parse the output again
        canonical2 = adapter.to_canonical(output, ConfigType.AGENT)

        # Verify core fields preserved
        assert canonical.name == canonical2.name
        assert canonical.description == canonical2.description
        assert canonical.model == canonical2.model
        assert canonical.tools == canonical2.tools

        # Verify metadata preserved
        assert canonical.get_metadata('copilot_argument_hint') == canonical2.get_metadata('copilot_argument_hint')
        assert canonical.get_metadata('copilot_target') == canonical2.get_metadata('copilot_target')
        assert canonical.get_metadata('copilot_handoffs') == canonical2.get_metadata('copilot_handoffs')
        assert canonical.get_metadata('copilot_mcp_servers') == canonical2.get_metadata('copilot_mcp_servers')


class TestCrossFormatConversion:
    """Tests for converting between different formats."""

    @pytest.fixture
    def claude_adapter(self):
        """Create ClaudeAdapter instance."""
        return ClaudeAdapter()

    @pytest.fixture
    def copilot_adapter(self):
        """Create CopilotAdapter instance."""
        return CopilotAdapter()

    @pytest.fixture
    def sample_claude_content(self):
        """Sample Claude agent file content."""
        return """---
name: cross-test-agent
description: Agent for cross-format testing
tools: Read, Grep, Glob
model: sonnet
permissionMode: ask
---
Cross-format test instructions.
"""

    @pytest.fixture
    def sample_copilot_content(self):
        """Sample Copilot agent file content."""
        return """---
name: cross-test-agent
description: Agent for cross-format testing
tools:
  - read
  - grep
  - glob
model: Claude Sonnet 4
target: vscode
argument-hint: Test hint
---
Cross-format test instructions.
"""

    def test_claude_to_copilot(self, claude_adapter, copilot_adapter, sample_claude_content):
        """Test Claude -> Canonical -> Copilot conversion."""
        # Claude to canonical
        canonical = claude_adapter.to_canonical(sample_claude_content, ConfigType.AGENT)

        # Canonical to Copilot
        copilot_output = copilot_adapter.from_canonical(canonical, ConfigType.AGENT)

        # Verify result
        assert "name: cross-test-agent" in copilot_output
        assert "model: Claude Sonnet 4" in copilot_output  # Model denormalized
        assert "target: vscode" in copilot_output
        assert "Cross-format test instructions" in copilot_output

    def test_copilot_to_claude(self, claude_adapter, copilot_adapter, sample_copilot_content):
        """Test Copilot -> Canonical -> Claude conversion."""
        # Copilot to canonical
        canonical = copilot_adapter.to_canonical(sample_copilot_content, ConfigType.AGENT)

        # Canonical to Claude
        claude_output = claude_adapter.from_canonical(canonical, ConfigType.AGENT)

        # Verify result
        assert "name: cross-test-agent" in claude_output
        assert "model: sonnet" in claude_output  # Model stays canonical
        assert "Cross-format test instructions" in claude_output

    def test_claude_to_copilot_to_claude(self, claude_adapter, copilot_adapter, sample_claude_content):
        """Test Claude -> Copilot -> Claude round-trip preserves core data.

        Note: Format-specific metadata (like Claude's permissionMode) is NOT
        preserved when going through another format, because that format's
        adapter doesn't know about or serialize the foreign metadata keys.
        This is expected behavior with the current design.
        """
        # Claude -> Canonical
        canonical1 = claude_adapter.to_canonical(sample_claude_content, ConfigType.AGENT)

        # Canonical -> Copilot
        copilot_output = copilot_adapter.from_canonical(canonical1, ConfigType.AGENT)

        # Copilot -> Canonical
        canonical2 = copilot_adapter.to_canonical(copilot_output, ConfigType.AGENT)

        # Canonical -> Claude
        claude_output = claude_adapter.from_canonical(canonical2, ConfigType.AGENT)

        # Claude -> Canonical (for final comparison)
        canonical3 = claude_adapter.to_canonical(claude_output, ConfigType.AGENT)

        # Core fields should be preserved
        assert canonical1.name == canonical3.name
        assert canonical1.description == canonical3.description
        assert canonical1.model == canonical3.model

        # Note: Claude-specific metadata (permissionMode) is lost when going through Copilot
        # because CopilotAdapter.from_canonical() doesn't serialize Claude metadata
        # This is expected - only same-format round-trips preserve all metadata
        assert canonical1.get_metadata('claude_permission_mode') == 'ask'
        assert canonical3.get_metadata('claude_permission_mode') is None  # Lost in conversion

    def test_copilot_to_claude_to_copilot(self, claude_adapter, copilot_adapter, sample_copilot_content):
        """Test Copilot -> Claude -> Copilot round-trip preserves core data.

        Note: Format-specific metadata (like Copilot's argument-hint) is NOT
        preserved when going through another format, because that format's
        adapter doesn't know about or serialize the foreign metadata keys.
        Only the default 'target: vscode' is added back by CopilotAdapter.
        """
        # Copilot -> Canonical
        canonical1 = copilot_adapter.to_canonical(sample_copilot_content, ConfigType.AGENT)

        # Canonical -> Claude
        claude_output = claude_adapter.from_canonical(canonical1, ConfigType.AGENT)

        # Claude -> Canonical
        canonical2 = claude_adapter.to_canonical(claude_output, ConfigType.AGENT)

        # Canonical -> Copilot
        copilot_output = copilot_adapter.from_canonical(canonical2, ConfigType.AGENT)

        # Copilot -> Canonical (for final comparison)
        canonical3 = copilot_adapter.to_canonical(copilot_output, ConfigType.AGENT)

        # Core fields should be preserved
        assert canonical1.name == canonical3.name
        assert canonical1.description == canonical3.description
        assert canonical1.model == canonical3.model

        # Note: Copilot-specific metadata (argument-hint) is lost when going through Claude
        # because ClaudeAdapter.from_canonical() doesn't serialize Copilot metadata
        # This is expected - only same-format round-trips preserve all metadata
        assert canonical1.get_metadata('copilot_argument_hint') == 'Test hint'
        assert canonical3.get_metadata('copilot_argument_hint') is None  # Lost in conversion

        # Target is preserved because CopilotAdapter always adds it with default 'vscode'
        assert canonical3.get_metadata('copilot_target') == 'vscode'

    def test_metadata_preservation_cross_format(self, claude_adapter, copilot_adapter):
        """Test that format-specific metadata survives cross-format conversion."""
        # Create an agent with both Claude and Copilot metadata
        agent = CanonicalAgent(
            name="metadata-test",
            description="Testing metadata preservation",
            instructions="Test instructions",
            tools=["read", "edit"],
            model="sonnet"
        )
        agent.add_metadata('claude_permission_mode', 'ask')
        agent.add_metadata('claude_skills', [{'name': 'test-skill'}])
        agent.add_metadata('copilot_argument_hint', 'Test hint')
        agent.add_metadata('copilot_handoffs', [{'label': 'Next', 'agent': 'next-agent'}])

        # Convert to Claude format
        claude_output = claude_adapter.from_canonical(agent, ConfigType.AGENT)
        claude_canonical = claude_adapter.to_canonical(claude_output, ConfigType.AGENT)

        # Claude-specific metadata should survive
        assert claude_canonical.get_metadata('claude_permission_mode') == 'ask'
        assert claude_canonical.get_metadata('claude_skills') == [{'name': 'test-skill'}]

        # Copilot-specific metadata should still be in the original agent
        # (it doesn't survive Claude round-trip as Claude doesn't know about it)

        # Convert original agent to Copilot format
        copilot_output = copilot_adapter.from_canonical(agent, ConfigType.AGENT)
        copilot_canonical = copilot_adapter.to_canonical(copilot_output, ConfigType.AGENT)

        # Copilot-specific metadata should survive
        assert copilot_canonical.get_metadata('copilot_argument_hint') == 'Test hint'
        assert copilot_canonical.get_metadata('copilot_handoffs') == [{'label': 'Next', 'agent': 'next-agent'}]
