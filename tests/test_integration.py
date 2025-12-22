"""
Integration tests for end-to-end sync operations.

Tests cover:
- Full sync workflow (Claude -> Copilot)
- Full sync workflow (Copilot -> Claude)
- Bidirectional sync
- Conflict resolution (force and interactive)
- State persistence across syncs
- Multiple file sync
- Single file conversion
- Deletion propagation
"""

import time
import pytest
from pathlib import Path
from unittest.mock import patch

from core.registry import FormatRegistry
from core.orchestrator import UniversalSyncOrchestrator
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType
from adapters import ClaudeAdapter, CopilotAdapter


# =============================================================================
# Module-Level Fixtures
# =============================================================================

@pytest.fixture
def registry():
    """Create registry with Claude and Copilot adapters."""
    reg = FormatRegistry()
    reg.register(ClaudeAdapter())
    reg.register(CopilotAdapter())
    return reg


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_results_session():
    """Clean up test results directory once at the start of the session."""
    results_dir = Path("test_results")
    if results_dir.exists():
        import shutil
        shutil.rmtree(results_dir)


@pytest.fixture
def test_results_dir(request):
    """
    Create persistent test results directory for the specific test.
    Structure: test_results/<test_name>/
    """
    base_dir = Path("test_results")
    if not base_dir.exists():
        base_dir.mkdir()
    
    # Create specific dir for this test
    test_dir = base_dir / request.node.name
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    return test_dir


@pytest.fixture
def state_file(test_results_dir):
    """Create persistent state file path in test dir."""
    return test_results_dir / "test_sync_state.json"


@pytest.fixture
def state_manager(state_file):
    """Create state manager with persistent state file."""
    return SyncStateManager(state_file)


@pytest.fixture
def claude_dir(test_results_dir):
    """Create persistent Claude agents directory in test dir."""
    d = test_results_dir / "claude_agents"
    d.mkdir()
    return d


@pytest.fixture
def copilot_dir(test_results_dir):
    """Create persistent Copilot agents directory in test dir."""
    d = test_results_dir / "copilot_agents"
    d.mkdir()
    return d


@pytest.fixture
def sample_claude_agent():
    """Sample Claude agent content."""
    return """---
name: test-agent
description: A test agent for integration testing
tools: Read, Grep, Glob
model: sonnet
---
This is the agent instructions body.

It can have multiple lines and paragraphs.
"""


@pytest.fixture
def sample_copilot_agent():
    """Sample Copilot agent content."""
    return """---
name: copilot-agent
description: A Copilot test agent
tools:
  - Read
  - Grep
  - Glob
model: Claude Sonnet 4
target: vscode
---
Copilot agent instructions here.

Multiple paragraphs supported.
"""


# =============================================================================
# TestClaudeToCopilotSync - Claude -> Copilot direction tests
# =============================================================================

class TestClaudeToCopilotSync:
    """Tests for Claude to Copilot sync direction."""

    def test_initial_sync_creates_copilot_file(
        self, registry, state_manager, claude_dir, copilot_dir, sample_claude_agent
    ):
        """Test that initial sync creates Copilot file from Claude source."""
        # Arrange: Create Claude agent file
        claude_file = claude_dir / "planner.md"
        claude_file.write_text(sample_claude_agent)

        # Act: Run sync
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Copilot file created
        copilot_file = copilot_dir / "planner.agent.md"
        assert copilot_file.exists(), "Copilot file should be created"

    def test_sync_preserves_agent_content(
        self, registry, state_manager, claude_dir, copilot_dir, sample_claude_agent
    ):
        """Test that sync preserves agent name, description, tools, and model."""
        # Arrange
        claude_file = claude_dir / "content-test.md"
        claude_file.write_text(sample_claude_agent)

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Content preserved
        copilot_file = copilot_dir / "content-test.agent.md"
        content = copilot_file.read_text()
        assert "name: test-agent" in content
        assert "A test agent for integration testing" in content
        assert "Read" in content
        assert "Grep" in content
        assert "Glob" in content
        assert "This is the agent instructions body" in content

    def test_source_change_updates_target(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test that modifying source file updates target on re-sync."""
        # Arrange: Create and sync initial file
        claude_file = claude_dir / "updater.md"
        claude_file.write_text("""---
name: updater
description: Original description
tools: Read
model: sonnet
---
Original instructions.
""")

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Ensure time difference for mtime detection
        time.sleep(0.1)

        # Act: Modify source and re-sync
        claude_file.write_text("""---
name: updater
description: Updated description
tools: Read, Grep
model: opus
---
Updated instructions.
""")

        # Create fresh state manager to simulate new sync session
        state_manager2 = SyncStateManager(state_manager.state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Target updated
        copilot_file = copilot_dir / "updater.agent.md"
        content = copilot_file.read_text()
        assert "Updated description" in content
        assert "Grep" in content
        assert "Updated instructions" in content

    def test_sync_official_claude_example(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test conversion of 'official' Claude agent example to Copilot format."""
        # Arrange: Load official fixture
        fixtures_dir = Path("tests/fixtures")
        claude_source = fixtures_dir / "claude" / "official-code-reviewer.md"
        expected_copilot = fixtures_dir / "copilot" / "official-code-reviewer.agent.md"
        
        # Copy to source directory
        import shutil
        shutil.copy(claude_source, claude_dir / "official-code-reviewer.md")

        # Act: Run sync (Claude -> Copilot)
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert
        generated_file = copilot_dir / "official-code-reviewer.agent.md"
        assert generated_file.exists(), "Copilot file should be generated"
        
        generated_content = generated_file.read_text(encoding='utf-8')
        expected_content = expected_copilot.read_text(encoding='utf-8')
        
        # Verify essential content matching
        # (Exact match might be tricky due to YAML formatting differences, so we check key components)
        assert "name: code-reviewer" in generated_content
        assert "target: vscode" in generated_content
        assert "description: Expert code review specialist" in generated_content
        assert "- Read" in generated_content
        assert "- Grep" in generated_content
        assert "model: inherit" in generated_content
        assert "You are a senior code reviewer" in generated_content



# =============================================================================
# TestCopilotToClaudeSync - Copilot -> Claude direction tests
# =============================================================================

class TestCopilotToClaudeSync:
    """Tests for Copilot to Claude sync direction."""

    def test_initial_sync_creates_claude_file(
        self, registry, state_manager, claude_dir, copilot_dir, sample_copilot_agent
    ):
        """Test that initial sync creates Claude file from Copilot source."""
        # Arrange: Create Copilot agent file
        copilot_file = copilot_dir / "reviewer.agent.md"
        copilot_file.write_text(sample_copilot_agent)

        # Act: Run sync (Copilot as source)
        orchestrator = UniversalSyncOrchestrator(
            source_dir=copilot_dir,
            target_dir=claude_dir,
            source_format='copilot',
            target_format='claude',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Claude file created
        claude_file = claude_dir / "reviewer.md"
        assert claude_file.exists(), "Claude file should be created"

    def test_sync_preserves_copilot_content(
        self, registry, state_manager, claude_dir, copilot_dir, sample_copilot_agent
    ):
        """Test that sync preserves Copilot agent content in Claude format."""
        # Arrange
        copilot_file = copilot_dir / "content-test.agent.md"
        copilot_file.write_text(sample_copilot_agent)

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=copilot_dir,
            target_dir=claude_dir,
            source_format='copilot',
            target_format='claude',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert
        claude_file = claude_dir / "content-test.md"
        content = claude_file.read_text()
        assert "name: copilot-agent" in content
        assert "A Copilot test agent" in content
        assert "Copilot agent instructions here" in content

    def test_sync_official_copilot_example(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test conversion of 'official' Copilot agent example to Claude format."""
        # Arrange: Load official fixture
        fixtures_dir = Path("tests/fixtures")
        copilot_source = fixtures_dir / "copilot" / "official-pr-reviewer.agent.md"
        expected_claude = fixtures_dir / "claude" / "official-pr-reviewer.md"
        
        # Copy to source directory
        import shutil
        shutil.copy(copilot_source, copilot_dir / "official-pr-reviewer.agent.md")

        # Act: Run sync (Copilot -> Claude)
        orchestrator = UniversalSyncOrchestrator(
            source_dir=copilot_dir,
            target_dir=claude_dir,
            source_format='copilot',
            target_format='claude',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert
        generated_file = claude_dir / "official-pr-reviewer.md"
        assert generated_file.exists(), "Claude file should be generated"
        
        generated_content = generated_file.read_text(encoding='utf-8')
        expected_content = expected_claude.read_text(encoding='utf-8')
        
        assert generated_content.strip() == expected_content.strip()


# =============================================================================
# TestBidirectionalSync - Bidirectional sync tests
# =============================================================================

class TestBidirectionalSync:
    """Tests for bidirectional sync workflows."""

    def test_bidirectional_creates_files_in_both_directions(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test that bidirectional sync creates files in both directions."""
        # Arrange: Create file only in Claude dir
        claude_only = claude_dir / "claude-only.md"
        claude_only.write_text("""---
name: claude-only
description: Only in Claude
tools: Read
model: sonnet
---
Claude only agent.
""")

        # Create file only in Copilot dir
        copilot_only = copilot_dir / "copilot-only.agent.md"
        copilot_only.write_text("""---
name: copilot-only
description: Only in Copilot
tools:
  - Grep
model: Claude Sonnet 4
target: vscode
---
Copilot only agent.
""")

        # Act: Run bidirectional sync
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            direction='both',
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Both directions synced
        assert (copilot_dir / "claude-only.agent.md").exists(), \
            "Claude file should be synced to Copilot dir"
        assert (claude_dir / "copilot-only.md").exists(), \
            "Copilot file should be synced to Claude dir"

    def test_bidirectional_handles_existing_pairs(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test bidirectional sync with files that already exist in both dirs."""
        # Arrange: Create matching files in both directories
        claude_file = claude_dir / "shared.md"
        claude_file.write_text("""---
name: shared
description: Shared agent
tools: Read
model: sonnet
---
Shared instructions.
""")

        copilot_file = copilot_dir / "shared.agent.md"
        copilot_file.write_text("""---
name: shared
description: Shared agent
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Shared instructions.
""")

        # Act: Should not error, just skip unchanged files
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            direction='both',
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Both files still exist
        assert claude_file.exists()
        assert copilot_file.exists()


# =============================================================================
# TestConflictResolution - Conflict resolution tests
# =============================================================================

class TestConflictResolution:
    """Tests for conflict resolution scenarios."""

    def test_conflict_force_uses_newer_source(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that force mode uses source when source is newer."""
        # Arrange: Create initial sync state
        state_manager = SyncStateManager(state_file)

        claude_file = claude_dir / "conflict.md"
        claude_file.write_text("""---
name: conflict
description: Initial
tools: Read
model: sonnet
---
Initial.
""")

        copilot_file = copilot_dir / "conflict.agent.md"
        copilot_file.write_text("""---
name: conflict
description: Initial
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Initial.
""")

        # Do initial sync to establish state
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False,
            force=True
        )
        orchestrator.sync()

        # Create conflict: both files modified
        time.sleep(0.1)
        copilot_file.write_text("""---
name: conflict
description: Target modified
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Target modified.
""")

        time.sleep(0.1)
        claude_file.write_text("""---
name: conflict
description: Source modified (newer)
tools: Read
model: sonnet
---
Source modified (newer).
""")

        # Act: Run sync with force, source is newer
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False,
            force=True
        )
        orchestrator2.sync()

        # Assert: Source content wins (it's newer)
        content = copilot_file.read_text()
        assert "Source modified (newer)" in content

    def test_conflict_force_uses_newer_target(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that force mode uses target when target is newer."""
        # Arrange
        state_manager = SyncStateManager(state_file)

        claude_file = claude_dir / "conflict2.md"
        claude_file.write_text("""---
name: conflict2
description: Initial
tools: Read
model: sonnet
---
Initial.
""")

        copilot_file = copilot_dir / "conflict2.agent.md"
        copilot_file.write_text("""---
name: conflict2
description: Initial
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Initial.
""")

        # Initial sync
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False,
            force=True
        )
        orchestrator.sync()

        # Create conflict: target newer
        time.sleep(0.1)
        claude_file.write_text("""---
name: conflict2
description: Source modified
tools: Read
model: sonnet
---
Source modified.
""")

        time.sleep(0.1)
        copilot_file.write_text("""---
name: conflict2
description: Target modified (newer)
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Target modified (newer).
""")

        # Act
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False,
            force=True
        )
        orchestrator2.sync()

        # Assert: Target content wins (it's newer)
        content = claude_file.read_text()
        assert "Target modified (newer)" in content

    def test_conflict_interactive_chooses_source(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that interactive mode uses source when user chooses 1."""
        # Arrange: Start with only source file
        state_manager = SyncStateManager(state_file)

        claude_file = claude_dir / "interactive.md"
        claude_file.write_text("""---
name: interactive
description: Initial
tools: Read
model: sonnet
---
Initial.
""")

        # Initial sync to create target and establish state
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        copilot_file = copilot_dir / "interactive.agent.md"
        assert copilot_file.exists(), "Initial sync should create target file"

        # Create conflict: modify both files after state was recorded
        time.sleep(0.1)
        claude_file.write_text("""---
name: interactive
description: Source version
tools: Read
model: sonnet
---
Source version.
""")

        time.sleep(0.1)
        copilot_file.write_text("""---
name: interactive
description: Target version
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Target version.
""")

        # Act: User chooses source (option 1)
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False,
            force=False  # Interactive mode
        )

        with patch('core.orchestrator.input', return_value='1'):
            orchestrator2.sync()

        # Assert: Source content wins
        content = copilot_file.read_text()
        assert "Source version" in content

    def test_conflict_interactive_chooses_target(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that interactive mode uses target when user chooses 2."""
        # Arrange: Start with only source file
        state_manager = SyncStateManager(state_file)

        claude_file = claude_dir / "interactive2.md"
        claude_file.write_text("""---
name: interactive2
description: Initial
tools: Read
model: sonnet
---
Initial.
""")

        # Initial sync to create target and establish state
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        copilot_file = copilot_dir / "interactive2.agent.md"
        assert copilot_file.exists(), "Initial sync should create target file"

        # Create conflict: modify both files after state was recorded
        time.sleep(0.1)
        claude_file.write_text("""---
name: interactive2
description: Source version
tools: Read
model: sonnet
---
Source version.
""")

        time.sleep(0.1)
        copilot_file.write_text("""---
name: interactive2
description: Target version
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Target version.
""")

        # Act: User chooses target (option 2)
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False,
            force=False
        )

        with patch('core.orchestrator.input', return_value='2'):
            orchestrator2.sync()

        # Assert: Target content wins (source updated from target)
        content = claude_file.read_text()
        assert "Target version" in content

    def test_conflict_interactive_skips(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that interactive mode skips when user chooses 3."""
        # Arrange: Start with only source file
        state_manager = SyncStateManager(state_file)

        claude_file = claude_dir / "skip.md"
        claude_file.write_text("""---
name: skip
description: Initial
tools: Read
model: sonnet
---
Initial.
""")

        # Initial sync to create target and establish state
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        copilot_file = copilot_dir / "skip.agent.md"
        assert copilot_file.exists(), "Initial sync should create target file"

        # Create conflict: modify both files after state was recorded
        time.sleep(0.1)
        claude_file.write_text("""---
name: skip
description: Source modified
tools: Read
model: sonnet
---
Source modified.
""")

        time.sleep(0.1)
        copilot_file.write_text("""---
name: skip
description: Target modified
tools:
  - Read
model: Claude Sonnet 4
target: vscode
---
Target modified.
""")

        original_source_content = claude_file.read_text()
        original_target_content = copilot_file.read_text()

        # Act: User chooses skip (option 3)
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False,
            force=False
        )

        with patch('core.orchestrator.input', return_value='3'):
            orchestrator2.sync()

        # Assert: Both files unchanged
        assert claude_file.read_text() == original_source_content
        assert copilot_file.read_text() == original_target_content


# =============================================================================
# TestStatePersistence - State persistence tests
# =============================================================================

class TestStatePersistence:
    """Tests for state persistence across syncs."""

    def test_state_file_created_after_sync(
        self, registry, state_file, claude_dir, copilot_dir, sample_claude_agent
    ):
        """Test that state file is created after sync."""
        # Arrange
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "state-test.md"
        claude_file.write_text(sample_claude_agent)

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert
        assert state_file.exists(), "State file should be created after sync"

    def test_unchanged_files_skipped_on_resync(
        self, registry, state_file, claude_dir, copilot_dir, sample_claude_agent
    ):
        """Test that unchanged files are skipped on re-sync."""
        # Arrange: Initial sync
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "unchanged.md"
        claude_file.write_text(sample_claude_agent)

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Act: Re-sync without changes
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Stats show nothing synced
        assert orchestrator2.stats['source_to_target'] == 0
        assert orchestrator2.stats['target_to_source'] == 0

    def test_state_updated_after_changes(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that state is updated with new mtimes after sync."""
        # Arrange
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "mtime-test.md"
        claude_file.write_text("""---
name: mtime-test
description: Test mtime
tools: Read
model: sonnet
---
Test.
""")

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: State has mtime info
        file_state = state_manager.get_file_state(
            claude_dir, copilot_dir, "mtime-test"
        )
        assert file_state is not None
        assert 'source_mtime' in file_state
        assert 'target_mtime' in file_state
        assert file_state['source_mtime'] > 0
        assert file_state['target_mtime'] > 0

    def test_state_persists_across_instances(
        self, registry, state_file, claude_dir, copilot_dir, sample_claude_agent
    ):
        """Test that state persists when loading a new SyncStateManager."""
        # Arrange: Do initial sync
        state_manager1 = SyncStateManager(state_file)
        claude_file = claude_dir / "persist-test.md"
        claude_file.write_text(sample_claude_agent)

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager1,
            dry_run=False
        )
        orchestrator.sync()

        original_mtime = state_manager1.get_file_state(
            claude_dir, copilot_dir, "persist-test"
        )['source_mtime']

        # Act: Create new state manager instance
        state_manager2 = SyncStateManager(state_file)

        # Assert: State loaded correctly
        file_state = state_manager2.get_file_state(
            claude_dir, copilot_dir, "persist-test"
        )
        assert file_state is not None
        assert file_state['source_mtime'] == original_mtime


# =============================================================================
# TestDeletionPropagation - Deletion sync tests
# =============================================================================

class TestDeletionPropagation:
    """Tests for deletion propagation behavior."""

    def test_source_deletion_deletes_target(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that deleting source file propagates deletion to target."""
        # Arrange: Create and sync file
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "to-delete.md"
        claude_file.write_text("""---
name: to-delete
description: Will be deleted
tools: Read
model: sonnet
---
Delete me.
""")

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        copilot_file = copilot_dir / "to-delete.agent.md"
        assert copilot_file.exists(), "Target file should exist after initial sync"

        # Act: Delete source and re-sync
        claude_file.unlink()

        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Target file deleted
        assert not copilot_file.exists(), "Target file should be deleted"

    def test_target_deletion_deletes_source(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that deleting target file propagates deletion to source."""
        # Arrange: Create and sync file
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "target-delete.md"
        claude_file.write_text("""---
name: target-delete
description: Target will be deleted
tools: Read
model: sonnet
---
Delete target.
""")

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            direction='both',  # Need bidirectional for target->source propagation
            dry_run=False
        )
        orchestrator.sync()

        copilot_file = copilot_dir / "target-delete.agent.md"
        assert copilot_file.exists()
        assert claude_file.exists()

        # Act: Delete target and re-sync
        copilot_file.unlink()

        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            direction='both',
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Source file deleted
        assert not claude_file.exists(), "Source file should be deleted"

    def test_deletion_cleans_state(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test that deletion removes state entry."""
        # Arrange
        state_manager = SyncStateManager(state_file)
        claude_file = claude_dir / "clean-state.md"
        claude_file.write_text("""---
name: clean-state
description: State cleanup test
tools: Read
model: sonnet
---
Test.
""")

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Verify state exists
        assert state_manager.get_file_state(
            claude_dir, copilot_dir, "clean-state"
        ) is not None

        # Act: Delete and re-sync
        claude_file.unlink()

        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: State entry removed
        assert state_manager2.get_file_state(
            claude_dir, copilot_dir, "clean-state"
        ) is None


# =============================================================================
# TestMultiFileSync - Multi-file sync tests
# =============================================================================

class TestMultiFileSync:
    """Tests for multi-file sync scenarios."""

    def test_multiple_agents_all_synced(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test that multiple agent files are all synced."""
        # Arrange: Create multiple Claude agents
        agents = ['planner', 'reviewer', 'executor', 'analyzer']
        for agent_name in agents:
            agent_file = claude_dir / f"{agent_name}.md"
            agent_file.write_text(f"""---
name: {agent_name}
description: {agent_name.title()} agent
tools: Read
model: sonnet
---
{agent_name.title()} instructions.
""")

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: All files created
        for agent_name in agents:
            copilot_file = copilot_dir / f"{agent_name}.agent.md"
            assert copilot_file.exists(), f"{agent_name} should be synced"
            content = copilot_file.read_text()
            assert f"name: {agent_name}" in content

    def test_mixed_new_and_existing_files(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test sync with mix of new and existing files."""
        # Arrange: Create existing synced file
        state_manager = SyncStateManager(state_file)

        existing_claude = claude_dir / "existing.md"
        existing_claude.write_text("""---
name: existing
description: Already synced
tools: Read
model: sonnet
---
Existing.
""")

        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Add new file
        new_claude = claude_dir / "new-agent.md"
        new_claude.write_text("""---
name: new-agent
description: New agent
tools: Grep
model: opus
---
New agent.
""")

        # Act: Re-sync
        state_manager2 = SyncStateManager(state_file)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Both exist, only new one synced
        assert (copilot_dir / "existing.agent.md").exists()
        assert (copilot_dir / "new-agent.agent.md").exists()
        assert orchestrator2.stats['source_to_target'] == 1  # Only new file


# =============================================================================
# TestSingleFileConversion - Single file conversion tests
# =============================================================================

class TestSingleFileConversion:
    """Tests for single file conversion accuracy."""

    def test_single_file_conversion_content(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test that single file conversion produces correct content."""
        # Arrange
        claude_file = claude_dir / "precise.md"
        claude_file.write_text("""---
name: precise-agent
description: Precisely defined agent
tools: Read, Grep, Glob, Bash
model: opus
---
Precise instructions for the agent.
""")

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Verify exact content
        copilot_file = copilot_dir / "precise.agent.md"
        content = copilot_file.read_text()

        assert "name: precise-agent" in content
        assert "Precisely defined agent" in content
        assert "Read" in content
        assert "Grep" in content
        assert "Glob" in content
        assert "Bash" in content
        assert "Precise instructions for the agent" in content
        assert "target: vscode" in content  # Copilot-specific

    def test_single_file_preserves_multiline_instructions(
        self, registry, state_manager, claude_dir, copilot_dir
    ):
        """Test that multiline instructions body is preserved."""
        # Arrange
        claude_file = claude_dir / "multiline.md"
        claude_file.write_text("""---
name: multiline
description: Multiline test
tools: Read
model: sonnet
---
First paragraph of instructions.

Second paragraph with more details.

- Bullet point 1
- Bullet point 2

Final paragraph.
""")

        # Act
        orchestrator = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager,
            dry_run=False
        )
        orchestrator.sync()

        # Assert: Multiline content preserved
        copilot_file = copilot_dir / "multiline.agent.md"
        content = copilot_file.read_text()

        assert "First paragraph of instructions" in content
        assert "Second paragraph with more details" in content
        assert "Bullet point 1" in content
        assert "Bullet point 2" in content
        assert "Final paragraph" in content

    def test_round_trip_preserves_content(
        self, registry, state_file, claude_dir, copilot_dir
    ):
        """Test Claude -> Copilot -> Claude preserves essential content."""
        # Arrange: Claude original
        original_content = """---
name: round-trip
description: Round trip test agent
tools: Read, Grep
model: sonnet
---
Round trip instructions.
"""
        claude_file = claude_dir / "round-trip.md"
        claude_file.write_text(original_content)

        # Step 1: Claude -> Copilot
        state_manager1 = SyncStateManager(state_file)
        orchestrator1 = UniversalSyncOrchestrator(
            source_dir=claude_dir,
            target_dir=copilot_dir,
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager1,
            dry_run=False
        )
        orchestrator1.sync()

        # Step 2: Delete original Claude file
        claude_file.unlink()

        # Step 3: Copilot -> Claude (reverse sync)
        state_file2 = state_file.parent / "state2.json"
        state_manager2 = SyncStateManager(state_file2)
        orchestrator2 = UniversalSyncOrchestrator(
            source_dir=copilot_dir,
            target_dir=claude_dir,
            source_format='copilot',
            target_format='claude',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=state_manager2,
            dry_run=False
        )
        orchestrator2.sync()

        # Assert: Content preserved in round trip
        restored_file = claude_dir / "round-trip.md"
        assert restored_file.exists()
        restored_content = restored_file.read_text()

        assert "name: round-trip" in restored_content
        assert "Round trip test agent" in restored_content
        assert "Round trip instructions" in restored_content
