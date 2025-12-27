"""
Universal sync orchestrator for coordinating multi-format synchronization.

The orchestrator is responsible for:
- Discovering file pairs across formats
- Determining sync actions (which direction, conflicts, deletions)
- Executing conversions via adapters
- Conflict resolution (interactive or automatic)
- Dry-run mode
- Statistics and reporting

This replaces the format-specific AgentSyncer with a universal version
that works with any formats through the adapter interface.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .canonical_models import ConfigType
from .registry import FormatRegistry
from .state_manager import SyncStateManager


@dataclass
class FilePair:
    """
    Represents a matched pair of files across formats.

    Attributes:
        base_name: Common identifier (e.g., 'planner' for planner.md <-> planner.agent.md)
        source_path: Path to source file (or None if doesn't exist)
        target_path: Path to target file (or None if doesn't exist)
        source_mtime: Source file modification time
        target_mtime: Target file modification time
    """
    base_name: str
    source_path: Optional[Path]
    target_path: Optional[Path]
    source_mtime: Optional[float]
    target_mtime: Optional[float]


class UniversalSyncOrchestrator:
    """
    Orchestrates synchronization between any two formats.

    This is the main entry point for sync operations. It coordinates:
    1. File discovery and matching
    2. Change detection via state manager
    3. Conflict resolution
    4. Format conversion via adapters
    5. Statistics tracking

    Example:
        registry = FormatRegistry()
        registry.register(ClaudeAdapter())
        registry.register(CopilotAdapter())

        orchestrator = UniversalSyncOrchestrator(
            source_dir=Path('~/.claude/agents'),
            target_dir=Path('.github/agents'),
            source_format='claude',
            target_format='copilot',
            config_type=ConfigType.AGENT,
            format_registry=registry,
            state_manager=SyncStateManager()
        )

        orchestrator.sync()
    """

    def __init__(self,
                 source_dir: Path,
                 target_dir: Path,
                 source_format: str,
                 target_format: str,
                 config_type: ConfigType,
                 format_registry: FormatRegistry,
                 state_manager: SyncStateManager,
                 direction: str = 'both',
                 dry_run: bool = False,
                 force: bool = False,
                 verbose: bool = False,
                 conversion_options: Optional[Dict[str, Any]] = None,
                 logger: Optional[Any] = None,
                 conflict_resolver: Optional[Any] = None):
        """
        Initialize sync orchestrator.

        Args:
            source_dir: Primary source directory
            target_dir: Primary target directory
            source_format: Source format name (e.g., 'claude')
            target_format: Target format name (e.g., 'copilot')
            config_type: Type of config to sync (AGENT, PERMISSION, SLASH_COMMAND)
            format_registry: Registry containing adapters
            state_manager: State tracking manager
            direction: 'both', 'source-to-target', or 'target-to-source'
            dry_run: If True, don't actually modify files
            force: If True, auto-resolve conflicts using newest file
            verbose: If True, print detailed logs
            conversion_options: Options to pass to adapters (e.g., add_argument_hint)
            logger: Callback for logging output (default: print)
            conflict_resolver: Callback for resolving conflicts (default: CLI interactive)
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.source_format = source_format
        self.target_format = target_format
        self.config_type = config_type
        self.registry = format_registry
        self.state_manager = state_manager
        self.direction = direction
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        self.conversion_options = conversion_options or {}
        self.logger = logger or print
        self.conflict_resolver = conflict_resolver or self._default_cli_conflict_resolver

        # Get adapters from registry
        self.source_adapter = format_registry.get_adapter(source_format)
        self.target_adapter = format_registry.get_adapter(target_format)

        if not self.source_adapter:
            raise ValueError(f"Unknown source format: {source_format}")
        if not self.target_adapter:
            raise ValueError(f"Unknown target format: {target_format}")

        # Validate config type support
        if config_type not in self.source_adapter.supported_config_types:
            raise ValueError(f"Format '{source_format}' does not support {config_type.value}")
        if config_type not in self.target_adapter.supported_config_types:
            raise ValueError(f"Format '{target_format}' does not support {config_type.value}")

        # Statistics
        self.stats = {
            'source_to_target': 0,
            'target_to_source': 0,
            'deletions': 0,
            'conflicts': 0,
            'skipped': 0,
            'errors': 0
        }

    def sync(self):
        """
        Execute sync operation.

        Main orchestration method that:
        1. Discovers file pairs
        2. Determines actions for each pair
        3. Resolves conflicts
        4. Executes conversions
        5. Updates state
        6. Reports statistics
        """
        self.log(f"Syncing {self.config_type.value}s: {self.direction}")
        self.log(f"  Source:  {self.source_dir} ({self.source_format})")
        self.log(f"  Target:  {self.target_dir} ({self.target_format})")
        if self.dry_run:
            self.log("  Mode: DRY RUN (no changes will be made)")
        self.logger()

        # Discover file pairs
        pairs = self._discover_file_pairs()

        if not pairs:
            self.logger("No files found in either directory.")
            self._print_summary()
            return

        # Process each pair
        for pair in pairs:
            action = self._determine_action(pair)

            if action == 'skip':
                if self.verbose:
                    self.logger(f"  Skip: {pair.base_name} (no changes)")
                self.stats['skipped'] += 1
                continue

            if action == 'conflict':
                self.stats['conflicts'] += 1
                resolved_action = self._resolve_conflict(pair)
                if not resolved_action:
                    self.logger(f"  Skip: {pair.base_name} (conflict skipped)")
                    self.stats['skipped'] += 1
                    continue
                action = resolved_action

            # Display action being performed
            action_display = {
                'source_to_target': f"{self.source_format} -> {self.target_format}",
                'target_to_source': f"{self.target_format} -> {self.source_format}",
                'delete_target': f"Delete from {self.target_format}",
                'delete_source': f"Delete from {self.source_format}"
            }
            prefix = "[DRY-RUN] " if self.dry_run else ""
            self.logger(f"{prefix}{pair.base_name}: {action_display.get(action, action)}")

            # Execute the sync action
            self._execute_sync_action(pair, action)

        # Save state (unless dry run)
        if not self.dry_run:
            self.state_manager.save()

        # Print summary
        self._print_summary()

    def _discover_file_pairs(self) -> List[FilePair]:
        """
        Discover and match files between source and target directories.

        Returns:
            List of FilePair objects representing matched files
        """
        files_by_base_name: Dict[str, Dict[str, Any]] = {}

        # Discover source files
        source_extension = self.source_adapter.get_file_extension(self.config_type)
        source_pattern = f"*{source_extension}"
        for file_path in self.source_dir.glob(source_pattern):
            if not self.source_adapter.can_handle(file_path):
                continue
            base_name = self._extract_base_name(file_path, source_extension)
            files_by_base_name[base_name] = {
                'source_path': file_path,
                'source_mtime': file_path.stat().st_mtime,
                'target_path': None,
                'target_mtime': None
            }

        # Discover target files
        target_extension = self.target_adapter.get_file_extension(self.config_type)
        target_pattern = f"*{target_extension}"
        for file_path in self.target_dir.glob(target_pattern):
            if not self.target_adapter.can_handle(file_path):
                continue
            base_name = self._extract_base_name(file_path, target_extension)
            if base_name in files_by_base_name:
                files_by_base_name[base_name]['target_path'] = file_path
                files_by_base_name[base_name]['target_mtime'] = file_path.stat().st_mtime
            else:
                files_by_base_name[base_name] = {
                    'source_path': None,
                    'source_mtime': None,
                    'target_path': file_path,
                    'target_mtime': file_path.stat().st_mtime
                }

        # Convert to FilePair list, sorted by base name
        return [
            FilePair(
                base_name=name,
                source_path=data['source_path'],
                target_path=data['target_path'],
                source_mtime=data['source_mtime'],
                target_mtime=data['target_mtime']
            )
            for name, data in sorted(files_by_base_name.items())
        ]

    def _determine_action(self, pair: FilePair) -> str:
        """
        Determine what sync action is needed for a file pair.

        Args:
            pair: FilePair to analyze

        Returns:
            Action string: 'source_to_target', 'target_to_source', 'conflict',
                          'delete_target', 'delete_source', or 'skip'
        """
        file_state = self.state_manager.get_file_state(
            self.source_dir, self.target_dir, pair.base_name
        )

        # DELETION: Source was deleted (state shows it existed, target still exists)
        if not pair.source_path and pair.target_path and file_state and file_state.get('source_mtime'):
            if self.direction in ['both', 'source-to-target']:
                return 'delete_target'
            return 'skip'

        # DELETION: Target was deleted (state shows it existed, source still exists)
        if not pair.target_path and pair.source_path and file_state and file_state.get('target_mtime'):
            if self.direction in ['both', 'target-to-source']:
                return 'delete_source'
            return 'skip'

        # BOTH DELETED: Both files gone but state exists
        if not pair.source_path and not pair.target_path:
            return 'skip'

        # NEW FILE: Source only (no target, no prior state)
        if pair.source_path and not pair.target_path:
            if self.direction in ['both', 'source-to-target']:
                return 'source_to_target'
            return 'skip'

        # NEW FILE: Target only (no source, no prior state)
        if pair.target_path and not pair.source_path:
            if self.direction in ['both', 'target-to-source']:
                return 'target_to_source'
            return 'skip'

        # BOTH FILES EXIST
        if pair.source_path and pair.target_path:
            if not file_state:
                # First sync - use newer file
                if pair.source_mtime > pair.target_mtime:
                    if self.direction in ['both', 'source-to-target']:
                        return 'source_to_target'
                    return 'skip'
                elif pair.target_mtime > pair.source_mtime:
                    if self.direction in ['both', 'target-to-source']:
                        return 'target_to_source'
                    return 'skip'
                return 'skip'  # Same mtime

            # Check changes since last sync
            last_source_mtime = file_state.get('source_mtime')
            last_target_mtime = file_state.get('target_mtime')

            # Use epsilon for float comparison to avoid precision issues
            epsilon = 0.01
            source_changed = last_source_mtime is None or pair.source_mtime > (last_source_mtime + epsilon)
            target_changed = last_target_mtime is None or pair.target_mtime > (last_target_mtime + epsilon)

            if source_changed and target_changed:
                return 'conflict'

            if source_changed:
                if self.direction in ['both', 'source-to-target']:
                    return 'source_to_target'
                return 'skip'

            if target_changed:
                if self.direction in ['both', 'target-to-source']:
                    return 'target_to_source'
                return 'skip'

        return 'skip'  # No changes

    def _default_cli_conflict_resolver(self, pair: FilePair) -> Optional[str]:
        """Default interactive CLI conflict resolver."""
        print(f"\nCONFLICT: Both files modified for '{pair.base_name}'")
        print(f"  Source: {pair.source_path}")
        print(f"    Modified: {datetime.fromtimestamp(pair.source_mtime)}")
        print(f"  Target: {pair.target_path}")
        print(f"    Modified: {datetime.fromtimestamp(pair.target_mtime)}")
        print("\nChoose action:")
        print(f"  1. Use source version ({self.source_format})")
        print(f"  2. Use target version ({self.target_format})")
        print("  3. Skip this file")

        while True:
            choice = input("Enter choice (1/2/3): ").strip()
            if choice == '1':
                return 'source_to_target'
            elif choice == '2':
                return 'target_to_source'
            elif choice == '3':
                return None
            print("Invalid choice. Enter 1, 2, or 3.")

    def _resolve_conflict(self, pair: FilePair) -> Optional[str]:
        """
        Resolve sync conflict interactively or automatically.

        Args:
            pair: FilePair with conflict

        Returns:
            Resolved action or None to skip
        """
        if self.force:
            # Handle None mtimes (treat as 0/oldest)
            source_mtime = pair.source_mtime or 0
            target_mtime = pair.target_mtime or 0

            # Use newest file
            if source_mtime > target_mtime:
                self.log(f"  Conflict resolved (--force): Using source (newer)")
                return 'source_to_target'
            else:
                self.log(f"  Conflict resolved (--force): Using target (newer)")
                return 'target_to_source'

        return self.conflict_resolver(pair)

    def _execute_sync_action(self, pair: FilePair, action: str):
        """
        Execute sync action for a file pair.

        Args:
            pair: FilePair to sync
            action: Action to execute
        """
        try:
            if action == 'source_to_target':
                # Race condition check: Verify target hasn't changed since discovery
                if pair.target_path and pair.target_path.exists():
                    current_mtime = pair.target_path.stat().st_mtime
                    if pair.target_mtime and current_mtime > pair.target_mtime:
                        self.logger(f"  Skipped: {pair.base_name} (Target modified since discovery)")
                        self.stats['skipped'] += 1
                        return

                # Read source and convert to canonical
                canonical = self.source_adapter.read(pair.source_path, self.config_type)

                # Determine target path
                target_path = pair.target_path
                if target_path is None:
                    target_extension = self.target_adapter.get_file_extension(self.config_type)
                    target_path = self.target_dir / f"{pair.base_name}{target_extension}"

                # Write to target (unless dry run)
                if not self.dry_run:
                    try:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        raise IOError(f"Failed to create directory {target_path.parent}: {e}")

                    self.target_adapter.write(canonical, target_path, self.config_type,
                                              self.conversion_options)
                    
                    if not target_path.exists():
                        raise IOError(f"Adapter write failed: file not found at {target_path}")

                    target_mtime = target_path.stat().st_mtime
                else:
                    # In dry-run, use existing mtime or current time for new files
                    target_mtime = pair.target_mtime or datetime.now().timestamp()

                # Log conversion warnings
                for warning in self.source_adapter.get_warnings():
                    self.log(f"  Warning: {warning}")
                self.source_adapter.clear_conversion_warnings()

                for warning in self.target_adapter.get_warnings():
                    self.log(f"  Warning: {warning}")
                self.target_adapter.clear_conversion_warnings()

                # Update state (unless dry run)
                if not self.dry_run:
                    self.state_manager.update_file_state(
                        self.source_dir, self.target_dir, pair.base_name,
                        pair.source_mtime, target_mtime, 'source_to_target',
                        self.source_format, self.target_format, self.config_type.value
                    )

                self.stats['source_to_target'] += 1

            elif action == 'target_to_source':
                # Race condition check: Verify source hasn't changed since discovery
                if pair.source_path and pair.source_path.exists():
                    current_mtime = pair.source_path.stat().st_mtime
                    if pair.source_mtime and current_mtime > pair.source_mtime:
                        self.logger(f"  Skipped: {pair.base_name} (Source modified since discovery)")
                        self.stats['skipped'] += 1
                        return

                # Read target and convert to canonical
                canonical = self.target_adapter.read(pair.target_path, self.config_type)

                # Determine source path
                source_path = pair.source_path
                if source_path is None:
                    source_extension = self.source_adapter.get_file_extension(self.config_type)
                    source_path = self.source_dir / f"{pair.base_name}{source_extension}"

                # Write to source (unless dry run)
                if not self.dry_run:
                    try:
                        source_path.parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        raise IOError(f"Failed to create directory {source_path.parent}: {e}")

                    self.source_adapter.write(canonical, source_path, self.config_type,
                                              self.conversion_options)
                    
                    if not source_path.exists():
                        raise IOError(f"Adapter write failed: file not found at {source_path}")

                    source_mtime = source_path.stat().st_mtime
                else:
                    # In dry-run, use existing mtime or current time for new files
                    source_mtime = pair.source_mtime or datetime.now().timestamp()

                # Log conversion warnings
                for warning in self.source_adapter.get_warnings():
                    self.log(f"  Warning: {warning}")
                self.source_adapter.clear_conversion_warnings()

                for warning in self.target_adapter.get_warnings():
                    self.log(f"  Warning: {warning}")
                self.target_adapter.clear_conversion_warnings()

                # Update state (unless dry run)
                if not self.dry_run:
                    self.state_manager.update_file_state(
                        self.source_dir, self.target_dir, pair.base_name,
                        source_mtime, pair.target_mtime, 'target_to_source',
                        self.source_format, self.target_format, self.config_type.value
                    )

                self.stats['target_to_source'] += 1

            elif action == 'delete_target':
                if not self.dry_run and pair.target_path:
                    try:
                        pair.target_path.unlink()
                    except FileNotFoundError:
                        pass  # Already deleted, no action needed
                if not self.dry_run:
                    self.state_manager.remove_file_state(
                        self.source_dir, self.target_dir, pair.base_name
                    )
                self.stats['deletions'] += 1

            elif action == 'delete_source':
                if not self.dry_run and pair.source_path:
                    try:
                        pair.source_path.unlink()
                    except FileNotFoundError:
                        pass  # Already deleted, no action needed
                if not self.dry_run:
                    self.state_manager.remove_file_state(
                        self.source_dir, self.target_dir, pair.base_name
                    )
                self.stats['deletions'] += 1

        except (IOError, ValueError, RuntimeError) as e:
            self.logger(f"  Error syncing {pair.base_name}: {e}")
            self.stats['errors'] += 1
        except Exception as e:
            # Re-raise system exceptions
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            self.logger(f"  Unexpected error syncing {pair.base_name}: {e}")
            self.stats['errors'] += 1

    def log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            self.logger(message)

    def _print_summary(self):
        """Print sync statistics summary."""
        self.logger()
        self.logger("=" * 60)
        self.logger("Summary:")
        self.logger(f"  {self.source_format} -> {self.target_format}: {self.stats['source_to_target']}")
        self.logger(f"  {self.target_format} -> {self.source_format}: {self.stats['target_to_source']}")
        self.logger(f"  Deletions:  {self.stats['deletions']}")
        self.logger(f"  Conflicts:  {self.stats['conflicts']}")
        self.logger(f"  Skipped:    {self.stats['skipped']}")
        self.logger(f"  Errors:     {self.stats['errors']}")
        self.logger("=" * 60)
        if self.dry_run:
            self.logger()
            self.logger("This was a dry run. Use without --dry-run to apply changes.")

    def _extract_base_name(self, file_path: Path, extension: str) -> str:
        """
        Extract base name from file, handling compound extensions like .agent.md.

        Args:
            file_path: Path to the file
            extension: The extension to remove (e.g., '.md' or '.agent.md')

        Returns:
            Base name without the extension
        """
        if not file_path.name:
            return ""

        name = file_path.name

        # Normalize extension: ensure it starts with a dot if not empty
        if extension and not extension.startswith('.'):
            extension = '.' + extension

        if extension and name.endswith(extension):
            return name[:-len(extension)]

        # Fallback to stem for files without extension or non-matching extension
        # Path.stem handles .hidden files by returning the full name
        return file_path.stem