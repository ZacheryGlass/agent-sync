"""
Unit tests for CLI subcommand functionality.

Tests cover:
- Subcommand parsing (sync, init, watch, config)
- Backward compatibility with legacy flat-argument style
- Deprecation warnings for old style
- Placeholder commands return appropriate messages
- Default behavior when no arguments provided
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from cli.main import create_parser, main, setup_registry, EXIT_SUCCESS, EXIT_ERROR


class TestSubcommandParsing:
    """Tests for subcommand structure."""

    @pytest.fixture
    def parser(self):
        """Create argument parser instance."""
        registry = setup_registry()
        return create_parser(registry)

    @pytest.fixture
    def valid_source_dir(self, tmp_path):
        """Create a valid source directory."""
        source = tmp_path / "source"
        source.mkdir()
        return source

    @pytest.fixture
    def valid_target_dir(self, tmp_path):
        """Create a valid target directory."""
        target = tmp_path / "target"
        target.mkdir()
        return target

    def test_sync_subcommand_exists(self, parser):
        """Test that sync subcommand is available."""
        args = parser.parse_args(['sync', '--source-format', 'claude', '--target-format', 'copilot'])
        assert args.subcommand == 'sync'

    def test_init_subcommand_exists(self, parser):
        """Test that init subcommand is available."""
        args = parser.parse_args(['init'])
        assert args.subcommand == 'init'

    def test_watch_subcommand_exists(self, parser):
        """Test that watch subcommand is available."""
        args = parser.parse_args(['watch'])
        assert args.subcommand == 'watch'

    def test_config_subcommand_exists(self, parser):
        """Test that config subcommand is available."""
        args = parser.parse_args(['config'])
        assert args.subcommand == 'config'

    def test_sync_subcommand_accepts_all_flags(self, parser, valid_source_dir, valid_target_dir):
        """Test that sync subcommand accepts all sync-related flags."""
        args = parser.parse_args([
            'sync',
            '--source-dir', str(valid_source_dir),
            '--target-dir', str(valid_target_dir),
            '--source-format', 'claude',
            '--target-format', 'copilot',
            '--direction', 'both',
            '--dry-run',
            '--force',
            '--strict',
            '--verbose',
            '--only', 'agents',
            '--yes',
            '--add-argument-hint',
            '--add-handoffs',
        ])
        assert args.subcommand == 'sync'
        assert args.source_dir == valid_source_dir
        assert args.target_dir == valid_target_dir
        assert args.source_format == 'claude'
        assert args.target_format == 'copilot'
        assert args.direction == 'both'
        assert args.dry_run is True
        assert args.force is True
        assert args.strict is True
        assert args.verbose is True
        assert args.only == 'agents'
        assert args.yes is True
        assert args.add_argument_hint is True
        assert args.add_handoffs is True

    def test_no_subcommand_no_args_shows_help(self):
        """Test that no subcommand and no args shows help and exits successfully."""
        result = main([])
        assert result == EXIT_SUCCESS


class TestBackwardCompatibility:
    """Tests for backward compatibility with legacy flat-argument style."""

    @pytest.fixture
    def parser(self):
        """Create argument parser instance."""
        registry = setup_registry()
        return create_parser(registry)

    @pytest.fixture
    def valid_source_dir(self, tmp_path):
        """Create a valid source directory."""
        source = tmp_path / "source"
        source.mkdir()
        return source

    @pytest.fixture
    def valid_target_dir(self, tmp_path):
        """Create a valid target directory."""
        target = tmp_path / "target"
        target.mkdir()
        return target

    def test_legacy_mode_parses_correctly(self, parser, valid_source_dir, valid_target_dir):
        """Test that legacy flat-argument style is still parsed."""
        args = parser.parse_args([
            '--source-dir', str(valid_source_dir),
            '--target-dir', str(valid_target_dir),
            '--source-format', 'claude',
            '--target-format', 'copilot',
        ])
        # In legacy mode, subcommand is None
        assert args.subcommand is None
        assert args.source_dir == valid_source_dir
        assert args.target_dir == valid_target_dir
        assert args.source_format == 'claude'
        assert args.target_format == 'copilot'

    def test_legacy_mode_shows_deprecation_warning(self, valid_source_dir, valid_target_dir, capsys):
        """Test that legacy mode shows deprecation warning."""
        # Create a fake source directory with proper structure
        agents_dir = valid_source_dir / "agents"
        agents_dir.mkdir()
        
        # Create a simple agent file
        agent_file = agents_dir / "test.md"
        agent_file.write_text("---\ndescription: test\n---\nTest agent")
        
        result = main([
            '--source-dir', str(valid_source_dir),
            '--target-dir', str(valid_target_dir),
            '--source-format', 'claude',
            '--target-format', 'copilot',
            '--dry-run',
        ])
        
        captured = capsys.readouterr()
        assert "Warning: Using legacy flat-argument style is deprecated" in captured.err
        assert "version 3.0" in captured.err
        assert "agent-sync sync" in captured.err

    def test_legacy_convert_file_shows_deprecation(self, tmp_path, capsys):
        """Test that legacy --convert-file shows deprecation warning."""
        # Create a test file
        test_file = tmp_path / "test.md"
        test_file.write_text("---\ndescription: test\n---\nTest agent")
        
        result = main([
            '--convert-file', str(test_file),
            '--target-format', 'copilot',
            '--dry-run',
        ])
        
        captured = capsys.readouterr()
        assert "Warning: Using legacy flat-argument style is deprecated" in captured.err

    def test_legacy_sync_file_shows_deprecation(self, tmp_path, capsys):
        """Test that legacy --sync-file shows deprecation warning."""
        # Create test files
        source_file = tmp_path / "source.json"
        source_file.write_text('{"permissions": {"terminal": {"allow": []}}}')
        
        target_file = tmp_path / "target.json"
        target_file.write_text('{"github.copilot.chat.terminalContext.enabled": true}')
        
        result = main([
            '--sync-file', str(source_file),
            '--target-file', str(target_file),
            '--source-format', 'claude',
            '--target-format', 'copilot',
            '--only', 'permissions',
            '--dry-run',
        ])
        
        captured = capsys.readouterr()
        assert "Warning: Using legacy flat-argument style is deprecated" in captured.err


class TestPlaceholderCommands:
    """Tests for placeholder commands (init, watch, config)."""

    def test_init_command_returns_message(self, capsys):
        """Test that init command shows coming soon message."""
        result = main(['init'])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert "init" in captured.err
        assert "coming soon" in captured.err
        assert "agent-sync sync" in captured.err

    def test_watch_command_returns_message(self, capsys):
        """Test that watch command shows coming soon message."""
        result = main(['watch'])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert "watch" in captured.err
        assert "coming soon" in captured.err
        assert "agent-sync sync" in captured.err

    def test_config_command_returns_message(self, capsys):
        """Test that config command shows coming soon message."""
        result = main(['config'])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert "config" in captured.err
        assert "coming soon" in captured.err
        assert "command-line flags" in captured.err


class TestSubcommandFunctional:
    """Functional tests for sync subcommand."""

    @pytest.fixture
    def valid_source_dir(self, tmp_path):
        """Create a valid source directory with agent."""
        source = tmp_path / "source"
        source.mkdir()
        agents_dir = source / "agents"
        agents_dir.mkdir()
        
        # Create a simple agent file
        agent_file = agents_dir / "test.md"
        agent_file.write_text("---\ndescription: Test agent\n---\n\nTest instructions")
        
        return source

    @pytest.fixture
    def valid_target_dir(self, tmp_path):
        """Create a valid target directory."""
        target = tmp_path / "target"
        target.mkdir()
        return target

    def test_sync_subcommand_works(self, valid_source_dir, valid_target_dir):
        """Test that sync subcommand executes successfully."""
        result = main([
            'sync',
            '--source-dir', str(valid_source_dir),
            '--target-dir', str(valid_target_dir),
            '--source-format', 'claude',
            '--target-format', 'copilot',
            '--only', 'agents',
            '--dry-run',
        ])
        
        assert result == EXIT_SUCCESS

    def test_sync_subcommand_convert_file(self, tmp_path):
        """Test that sync subcommand works with --convert-file."""
        # Create a test file
        test_file = tmp_path / "test.md"
        test_file.write_text("---\nname: Test Agent\ndescription: Test agent\n---\n\nTest instructions")
        
        result = main([
            'sync',
            '--convert-file', str(test_file),
            '--target-format', 'copilot',
            '--dry-run',
        ])
        
        assert result == EXIT_SUCCESS

    def test_sync_with_no_deprecation_warning(self, valid_source_dir, valid_target_dir, capsys):
        """Test that using sync subcommand does NOT show deprecation warning."""
        result = main([
            'sync',
            '--source-dir', str(valid_source_dir),
            '--target-dir', str(valid_target_dir),
            '--source-format', 'claude',
            '--target-format', 'copilot',
            '--only', 'agents',
            '--dry-run',
        ])
        
        captured = capsys.readouterr()
        assert "deprecated" not in captured.err.lower()
