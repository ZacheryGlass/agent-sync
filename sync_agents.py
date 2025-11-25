#!/usr/bin/env python3
"""
Backward compatibility wrapper for the new universal sync architecture.

This script provides the same CLI interface as sync_custom_agents.py but uses
the new architecture under the hood. This allows gradual migration while
maintaining compatibility with existing workflows.

Usage:
    python sync_agents.py --claude-dir ~/.claude/agents --copilot-dir .github/agents

Status: STUB - To be implemented when orchestrator is complete

Migration path:
1. Keep sync_custom_agents.py functional (legacy implementation)
2. Implement this wrapper to use new architecture
3. Test both produce identical results
4. Deprecate sync_custom_agents.py
5. Eventually make this the default entry point
"""

import argparse
import sys
from pathlib import Path

# TODO: Import new architecture components when ready
# from core.registry import FormatRegistry
# from core.orchestrator import UniversalSyncOrchestrator
# from core.state_manager import SyncStateManager
# from core.canonical_models import ConfigType
# from adapters import ClaudeAdapter, CopilotAdapter


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser matching sync_custom_agents.py interface.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Sync custom agents between Claude Code and GitHub Copilot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initial migration (Claude → Copilot)
  %(prog)s --claude-dir ~/.claude/agents --copilot-dir ./.github/agents --direction claude-to-copilot

  # Bidirectional sync (default)
  %(prog)s --claude-dir ~/.claude/agents --copilot-dir ./.github/agents --force --verbose

  # Dry run to preview changes
  %(prog)s --claude-dir ~/.claude/agents --copilot-dir ./.github/agents --dry-run
        """
    )

    parser.add_argument(
        '--claude-dir',
        type=Path,
        required=True,
        help='Path to Claude Code agents directory'
    )

    parser.add_argument(
        '--copilot-dir',
        type=Path,
        required=True,
        help='Path to GitHub Copilot agents directory'
    )

    parser.add_argument(
        '--direction',
        choices=['claude-to-copilot', 'copilot-to-claude', 'both'],
        default='both',
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
        help='Verbose output'
    )

    parser.add_argument(
        '--add-argument-hint',
        action='store_true',
        help='Add argument-hint field when converting Claude → Copilot (uses description)'
    )

    parser.add_argument(
        '--add-handoffs',
        action='store_true',
        help='Add handoffs placeholder when converting Claude → Copilot'
    )

    return parser


def main(argv=None):
    """
    Main entry point using new architecture.

    This provides backward compatibility with sync_custom_agents.py interface
    while using the new universal sync architecture.

    Args:
        argv: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # TODO: Implement using new architecture
    # 1. Setup registry
    # registry = FormatRegistry()
    # registry.register(ClaudeAdapter())
    # registry.register(CopilotAdapter())
    #
    # 2. Map direction to new format
    # direction_map = {
    #     'claude-to-copilot': 'source-to-target',
    #     'copilot-to-claude': 'target-to-source',
    #     'both': 'both'
    # }
    #
    # 3. Create orchestrator
    # orchestrator = UniversalSyncOrchestrator(
    #     source_dir=args.claude_dir,
    #     target_dir=args.copilot_dir,
    #     source_format='claude',
    #     target_format='copilot',
    #     config_type=ConfigType.AGENT,
    #     format_registry=registry,
    #     state_manager=SyncStateManager(),
    #     direction=direction_map[args.direction],
    #     dry_run=args.dry_run,
    #     force=args.force,
    #     verbose=args.verbose,
    #     conversion_options={
    #         'add_argument_hint': args.add_argument_hint,
    #         'add_handoffs': args.add_handoffs
    #     }
    # )
    #
    # 4. Run sync
    # try:
    #     orchestrator.sync()
    #     return 0
    # except Exception as e:
    #     print(f"Error: {e}", file=sys.stderr)
    #     return 1

    print("Backward compatibility wrapper stub")
    print(f"Would sync: {args.claude_dir} <-> {args.copilot_dir}")
    print(f"Direction: {args.direction}")
    print("\nNote: This wrapper is not yet implemented.")
    print("Use sync_custom_agents.py for now.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
