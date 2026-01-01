"""
Tests for --strict flag behavior in bidirectional in-place sync.

This module tests that the --strict flag properly fails before any writes
when lossy conversions are detected in either direction during bidirectional sync.
"""

import json
import pytest

from core.orchestrator import UniversalSyncOrchestrator
from core.registry import FormatRegistry
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType, CanonicalPermission
from adapters import ClaudeAdapter, CopilotAdapter


class TestStrictBidirectionalSync:
    """Tests for strict mode in bidirectional in-place sync."""

    def test_strict_bidirectional_forward_warnings_prevents_all_writes(self, tmp_path):
        """Test that warnings in forward direction prevent both forward and backward writes."""
        # Setup: Create source with deny rule (will produce warning when converting to copilot)
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": ["git status"],
                "deny": ["Bash(rm:*)"],  # Correct format: Bash(pattern)
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        # Setup: Create target with different permissions
        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {
                "ls": True
            }
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        # Create registry and orchestrator with strict=True
        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="copilot",
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=True  # Enable strict mode
        )

        # Save original content for verification
        original_source = source_file.read_text()
        original_target = target_file.read_text()

        # Execute bidirectional sync - should raise ValueError
        with pytest.raises(ValueError, match="Lossy conversions detected with --strict flag"):
            orchestrator.sync_files_in_place(
                source_path=source_file,
                target_path=target_file,
                bidirectional=True,
                dry_run=False
            )

        # Verify NO files were modified
        assert source_file.read_text() == original_source
        assert target_file.read_text() == original_target

    def test_strict_bidirectional_backward_warnings_prevents_all_writes(self, tmp_path):
        """Test that warnings in backward direction prevent both forward and backward writes."""
        # Setup: Create source with clean permissions
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": ["git status"],
                "deny": [],
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        # Setup: Create target with deny rule that will produce warning when converting back
        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {
                "ls": True,
                "rm": False  # When converted to Claude, this is lossy if originally "deny"
            }
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        # Mock adapters to simulate warnings in backward direction
        registry = FormatRegistry()
        
        # Use real adapters but we'll need to trigger warnings somehow
        # For this test, we'll use a simpler approach with deny rules
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": [],
                "deny": [],
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        target_file = tmp_path / "target_settings.json"
        target_content = {
            "permissions": {
                "allow": [],
                "deny": ["bash -c"],  # This will warn in backward direction
                "ask": []
            }
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        registry.register(ClaudeAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="claude",  # Same format to focus on warning logic
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=True
        )

        # Save original content

        # This test scenario requires a more precise backward-direction warning setup.
        # Mark it as skipped for now to avoid running an incomplete test.
        pytest.skip("test_strict_bidirectional_backward_warnings_prevents_all_writes requires revision")
    def test_strict_unidirectional_warnings_prevents_write(self, tmp_path):
        """Test that warnings in unidirectional sync prevent writes."""
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": [],
                "deny": ["Bash(rm:*)"],  # Correct format
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {}
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="copilot",
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=True
        )

        original_target = target_file.read_text()

        # Execute unidirectional sync - should raise ValueError
        with pytest.raises(ValueError, match="Lossy conversions detected with --strict flag"):
            orchestrator.sync_files_in_place(
                source_path=source_file,
                target_path=target_file,
                bidirectional=False,
                dry_run=False
            )

        # Verify target was NOT modified
        assert target_file.read_text() == original_target

    def test_strict_no_warnings_allows_writes(self, tmp_path):
        """Test that strict mode allows writes when no warnings are present."""
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": ["Bash(git:*)"],  # Use proper format
                "deny": [],  # No deny rules = no warnings
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {
                "ls": True
            }
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="copilot",
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=True
        )

        # Execute bidirectional sync - should succeed
        orchestrator.sync_files_in_place(
            source_path=source_file,
            target_path=target_file,
            bidirectional=True,
            dry_run=False
        )

        # Verify files were modified (merged)
        result = json.loads(target_file.read_text())
        # Both rules should be present
        assert "git" in result["chat.tools.terminal.autoApprove"]
        assert "ls" in result["chat.tools.terminal.autoApprove"]

    def test_non_strict_with_warnings_allows_writes(self, tmp_path):
        """Test that non-strict mode allows writes even with warnings."""
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": [],
                "deny": ["Bash(rm:*)"],  # Correct format
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {}
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="copilot",
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=False  # Strict mode disabled
        )

        # Execute sync - should succeed despite warnings
        orchestrator.sync_files_in_place(
            source_path=source_file,
            target_path=target_file,
            bidirectional=False,
            dry_run=False
        )

        # Verify target WAS modified (warnings logged but not fatal)
        result = json.loads(target_file.read_text())
        assert "rm" in result["chat.tools.terminal.autoApprove"]
        assert result["chat.tools.terminal.autoApprove"]["rm"] == False

    def test_strict_dry_run_with_warnings_still_fails(self, tmp_path):
        """Test that strict mode with dry-run still checks warnings and fails."""
        source_file = tmp_path / "source_settings.json"
        source_content = {
            "permissions": {
                "allow": [],
                "deny": ["Bash(rm:*)"],  # Correct format
                "ask": []
            }
        }
        source_file.write_text(json.dumps(source_content, indent=2))

        target_file = tmp_path / "target_settings.perm.json"
        target_content = {
            "chat.tools.terminal.autoApprove": {}
        }
        target_file.write_text(json.dumps(target_content, indent=2))

        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=tmp_path,
            target_dir=tmp_path,
            source_format="claude",
            target_format="copilot",
            config_type=ConfigType.PERMISSION,
            format_registry=registry,
            state_manager=SyncStateManager(),
            strict=True
        )

        original_target = target_file.read_text()

        # Execute with dry-run - should still fail on warnings
        with pytest.raises(ValueError, match="Lossy conversions detected with --strict flag"):
            orchestrator.sync_files_in_place(
                source_path=source_file,
                target_path=target_file,
                bidirectional=False,
                dry_run=True
            )

        # Verify target was NOT modified (would not be in dry-run anyway)
        assert target_file.read_text() == original_target
