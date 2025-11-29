"""
Main CLI entry point for universal agent sync tool.

This module provides the command-line interface for syncing configurations
between different AI coding tools. It supports:
- Multi-format sync (Claude, Copilot, etc.)
- Multiple config types (agents, permissions, prompts)
- Bidirectional and unidirectional sync
- Dry-run mode
- Conflict resolution

Usage:
    python -m cli.main --source-dir ~/.claude/agents --target-dir .github/agents \
                       --source-format claude --target-format copilot \
                       --config-type agent --direction both
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from core.registry import FormatRegistry
from core.orchestrator import UniversalSyncOrchestrator
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType

# Import adapters
from adapters import ClaudeAdapter, CopilotAdapter


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
        choices=['claude', 'copilot'],
        help='Source format name'
    )

    parser.add_argument(
        '--target-format',
        type=str,
        required=True,
        choices=['claude', 'copilot'],
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

    try:
        # 1. Expand and validate paths
        source_dir = args.source_dir.expanduser().resolve()
        target_dir = args.target_dir.expanduser().resolve()

        if not source_dir.exists():
            print(f"Error: Source directory does not exist: {source_dir}", file=sys.stderr)
            return 1

        if not source_dir.is_dir():
            print(f"Error: Source path is not a directory: {source_dir}", file=sys.stderr)
            return 1

        # Target directory doesn't need to exist (will be created if needed)
        # but if it exists, it must be a directory
        if target_dir.exists() and not target_dir.is_dir():
            print(f"Error: Target path exists but is not a directory: {target_dir}", file=sys.stderr)
            return 1

        # 2. Convert config_type string to ConfigType enum
        config_type_map = {
            'agent': ConfigType.AGENT,
            'permission': ConfigType.PERMISSION,
            'prompt': ConfigType.PROMPT
        }
        config_type = config_type_map[args.config_type]

        # 3. Setup registry
        registry = setup_registry()

        # 4. Create state manager
        state_file = args.state_file.expanduser().resolve() if args.state_file else None
        state_manager = SyncStateManager(state_file=state_file)

        # 5. Build conversion options
        conversion_options = {}
        if args.add_argument_hint:
            conversion_options['add_argument_hint'] = True
        if args.add_handoffs:
            conversion_options['add_handoffs'] = True

        # 6. Create orchestrator
        orchestrator = UniversalSyncOrchestrator(
            source_dir=source_dir,
            target_dir=target_dir,
            source_format=args.source_format,
            target_format=args.target_format,
            config_type=config_type,
            format_registry=registry,
            state_manager=state_manager,
            direction=args.direction,
            dry_run=args.dry_run,
            force=args.force,
            verbose=args.verbose,
            conversion_options=conversion_options if conversion_options else None
        )

        # 7. Run sync
        orchestrator.sync()

        # Success
        return 0

    except KeyboardInterrupt:
        print("\nSync cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
