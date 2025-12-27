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
import os
import sys
from pathlib import Path
from typing import Optional

from core.registry import FormatRegistry
from core.orchestrator import UniversalSyncOrchestrator
from core.state_manager import SyncStateManager
from core.canonical_models import ConfigType

# Import adapters
from adapters import ClaudeAdapter, CopilotAdapter

# Mapping from CLI string to ConfigType enum (single source of truth)
CONFIG_TYPE_MAP = {
    'agent': ConfigType.AGENT,
    'permission': ConfigType.PERMISSION,
    'slash-command': ConfigType.SLASH_COMMAND
}


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

  # Sync Claude permissions to Copilot
  %(prog)s --source-dir ~/.claude --target-dir .github \\
           --source-format claude --target-format copilot \\
           --config-type permission

  # Sync Claude slash commands to Copilot
  %(prog)s --source-dir ~/.claude/commands --target-dir .github/prompts \\
           --source-format claude --target-format copilot \\
           --config-type slash-command

  # Bidirectional sync with dry-run
  %(prog)s --source-dir ~/.claude/agents --target-dir .github/agents \\
           --source-format claude --target-format copilot \\
           --config-type agent --direction both --dry-run
        """
    )

    # Single-file conversion mode
    parser.add_argument(
        '--convert-file',
        type=Path,
        help='Single file to convert (mutually exclusive with --source-dir)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path for single-file conversion (auto-generated if not specified)'
    )

    # Directory sync mode arguments (required for directory sync, not for file conversion)
    parser.add_argument(
        '--source-dir',
        type=Path,
        help='Source directory containing configuration files'
    )

    parser.add_argument(
        '--target-dir',
        type=Path,
        help='Target directory for synced configuration files'
    )

    # Format arguments (optional for auto-detection in file mode)
    parser.add_argument(
        '--source-format',
        type=str,
        choices=['claude', 'copilot'],
        help='Source format name (auto-detected if not specified)'
    )

    parser.add_argument(
        '--target-format',
        type=str,
        choices=['claude', 'copilot'],
        help='Target format name (auto-detected from output if not specified)'
    )

    # Optional arguments
    parser.add_argument(
        '--config-type',
        type=str,
        default='agent',
        choices=['agent', 'permission', 'slash-command'],
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

    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch the graphical user interface'
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


def convert_single_file(args) -> int:
    """
    Convert a single file from one format to another.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    registry = setup_registry()

    # 1. Validate source file
    source_file = args.convert_file.expanduser().resolve()
    if not source_file.exists():
        print(f"Error: File not found: {source_file}", file=sys.stderr)
        return 1
    if source_file.is_dir():
        print(f"Error: Path is a directory, not a file: {source_file}", file=sys.stderr)
        return 1

    # 2. Determine source adapter (explicit or auto-detect)
    if args.source_format:
        source_adapter = registry.get_adapter(args.source_format)
        if not source_adapter:
            print(f"Error: Unknown source format: {args.source_format}", file=sys.stderr)
            return 1
    else:
        source_adapter = registry.detect_format(source_file)
        if not source_adapter:
            print(f"Error: Cannot auto-detect format for: {source_file}", file=sys.stderr)
            return 1

    # 3. Determine target adapter (explicit or from output extension)
    if args.target_format:
        target_adapter = registry.get_adapter(args.target_format)
        if not target_adapter:
            print(f"Error: Unknown target format: {args.target_format}", file=sys.stderr)
            return 1
    elif args.output:
        target_adapter = registry.detect_format(args.output)
        if not target_adapter:
            print(f"Error: Cannot auto-detect target format from: {args.output}", file=sys.stderr)
            return 1
    else:
        print("Error: --target-format or --output required for conversion", file=sys.stderr)
        return 1

    # 4. Determine output path (explicit or auto-generate)
    if args.output:
        output_file = args.output.expanduser().resolve()
    else:
        # Auto-generate: same directory, base name + target extension
        base_name = source_file.stem
        # Handle .agent.md extension specially
        if source_file.name.endswith('.agent.md'):
            base_name = source_file.name[:-9]  # Remove .agent.md
        output_file = source_file.parent / f"{base_name}{target_adapter.file_extension}"

    # 5. Get config type
    config_type = CONFIG_TYPE_MAP[args.config_type]

    # 6. Build conversion options
    conversion_options = {}
    if getattr(args, 'add_argument_hint', False):
        conversion_options['add_argument_hint'] = True
    if getattr(args, 'add_handoffs', False):
        conversion_options['add_handoffs'] = True

    # 7. Perform conversion
    try:
        if args.verbose:
            print(f"Converting {source_file} -> {output_file}")
            print(f"  Source format: {source_adapter.format_name}")
            print(f"  Target format: {target_adapter.format_name}")

        # Read and convert to canonical
        canonical = source_adapter.read(source_file, config_type)

        # Convert to target format
        output_content = target_adapter.from_canonical(
            canonical, config_type, conversion_options if conversion_options else None
        )

        if args.dry_run:
            print(f"Would write to: {output_file}")
            if args.verbose:
                print("--- Output content ---")
                print(output_content)
            return 0

        # Write output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
        except PermissionError:
            print(f"Error: Permission denied writing to {output_file}", file=sys.stderr)
            return 1
        except FileNotFoundError:
            print(f"Error: Could not find directory for {output_file}", file=sys.stderr)
            return 1

        if args.verbose:
            print(f"Successfully converted to {output_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


def main(argv: Optional[list] = None):
    """
    Main entry point for CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if argv is None:
        argv = sys.argv[1:]

    # Check for GUI launch conditions:
    # 1. Explicit --gui flag
    # 2. No arguments provided (default to GUI)
    if '--gui' in argv or not argv:
        try:
            from gui.main import start as start_gui
            start_gui()
            return 0
        except ImportError as e:
            print(f"Error: Could not import GUI: {e}", file=sys.stderr)
            print("Ensure nicegui is installed: pip install nicegui", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error launching GUI: {e}", file=sys.stderr)
            return 1

    parser = create_parser()
    args = parser.parse_args(argv)

    # Route to single-file conversion mode if --convert-file is specified
    if args.convert_file:
        # Validate mutual exclusivity
        if args.source_dir:
            print("Error: --convert-file and --source-dir are mutually exclusive", file=sys.stderr)
            return 1
        return convert_single_file(args)

    # Directory sync mode - validate required arguments
    if not args.source_dir:
        print("Error: --source-dir is required for directory sync", file=sys.stderr)
        return 1
    if not args.target_dir:
        print("Error: --target-dir is required for directory sync", file=sys.stderr)
        return 1
    if not args.source_format:
        print("Error: --source-format is required for directory sync", file=sys.stderr)
        return 1
    if not args.target_format:
        print("Error: --target-format is required for directory sync", file=sys.stderr)
        return 1

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
        # but if it exists, it must be a directory and writable
        if target_dir.exists():
            if not target_dir.is_dir():
                print(f"Error: Target path exists but is not a directory: {target_dir}", file=sys.stderr)
                return 1
            if not os.access(target_dir, os.W_OK):
                print(f"Error: Target directory is not writable: {target_dir}", file=sys.stderr)
                return 1
        else:
            # If it doesn't exist, check if parent is writable
            if not os.access(target_dir.parent, os.W_OK):
                print(f"Error: Target parent directory is not writable: {target_dir.parent}", file=sys.stderr)
                return 1

        # 2. Convert config_type string to ConfigType enum
        config_type = CONFIG_TYPE_MAP[args.config_type]

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
