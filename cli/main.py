"""
Main CLI entry point for universal agent sync tool.

This module provides the command-line interface for syncing configurations
between different AI coding tools. It supports:
- Multi-format sync (Claude, Copilot, Cursor, etc.)
- Multiple config types (agents, permissions, prompts)
- Bidirectional and unidirectional sync
- Dry-run mode
- Conflict resolution

Usage:
    python -m cli.main --source-dir ~/.claude/agents --target-dir .github/agents \
                       --source-format claude --target-format copilot \
                       --config-type agent --direction both

Status: STUB - To be implemented with full argparse configuration
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from core.registry import FormatRegistry
from core.orchestrator import UniversalSyncOrchestrator
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType

# Import all adapters
from adapters import ClaudeAdapter, CopilotAdapter, CursorAdapter, WindsurfAdapter, ContinueAdapter


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Universal sync tool for AI coding agent configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync Claude agents to Copilot
  %(prog)s --source-dir ~/.claude/agents --target-dir .github/agents \\
           --source-format claude --target-format copilot \\
           --config-type agent

  # Bidirectional sync with dry-run
  %(prog)s --source-dir ~/.claude/agents --target-dir .github/agents \\
           --source-format claude --target-format copilot \\
           --config-type agent --direction both --dry-run

  # Multi-way sync (future feature)
  %(prog)s --sync-all --formats claude,copilot,cursor \\
           --config-type agent
        """
    )

    # Required arguments
    parser.add_argument(
        '--source-dir',
        type=Path,
        required=True,
        help='Source directory containing configuration files'
    )

    parser.add_argument(
        '--target-dir',
        type=Path,
        required=True,
        help='Target directory for synced configuration files'
    )

    parser.add_argument(
        '--source-format',
        type=str,
        required=True,
        choices=['claude', 'copilot', 'cursor', 'windsurf', 'continue'],
        help='Source format name'
    )

    parser.add_argument(
        '--target-format',
        type=str,
        required=True,
        choices=['claude', 'copilot', 'cursor', 'windsurf', 'continue'],
        help='Target format name'
    )

    # Optional arguments
    parser.add_argument(
        '--config-type',
        type=str,
        default='agent',
        choices=['agent', 'permission', 'prompt'],
        help='Type of configuration to sync (default: agent)'
    )

    parser.add_argument(
        '--direction',
        type=str,
        default='both',
        choices=['both', 'source-to-target', 'target-to-source'],
        help='Sync direction (default: both)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Auto-resolve conflicts using newest file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with detailed logging'
    )

    parser.add_argument(
        '--state-file',
        type=Path,
        help='Custom path for state file (default: ~/.agent_sync_state.json)'
    )

    # Conversion options
    parser.add_argument(
        '--add-argument-hint',
        action='store_true',
        help='[Copilot] Add argument-hint field when converting to Copilot'
    )

    parser.add_argument(
        '--add-handoffs',
        action='store_true',
        help='[Copilot] Add handoffs placeholder when converting to Copilot'
    )

    return parser


def setup_registry() -> FormatRegistry:
    """
    Initialize format registry with all available adapters.

    Returns:
        FormatRegistry with registered adapters
    """
    registry = FormatRegistry()

    # Register adapters
    registry.register(ClaudeAdapter())
    registry.register(CopilotAdapter())
    # Note: Cursor, Windsurf, Continue are stubs - will raise NotImplementedError
    registry.register(CursorAdapter())
    registry.register(WindsurfAdapter())
    registry.register(ContinueAdapter())

    return registry


def main(argv: Optional[list] = None):
    """
    Main entry point for CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # TODO: Implement full CLI logic
    # 1. Validate arguments
    # 2. Setup registry
    # 3. Create state manager
    # 4. Create orchestrator
    # 5. Run sync
    # 6. Handle errors
    # 7. Return exit code

    print("CLI stub - to be implemented")
    print(f"Would sync from {args.source_dir} ({args.source_format}) "
          f"to {args.target_dir} ({args.target_format})")
    print(f"Config type: {args.config_type}, Direction: {args.direction}")

    if args.dry_run:
        print("Dry-run mode enabled")

    return 0


if __name__ == '__main__':
    sys.exit(main())
