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
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from .adapter_interface import FormatAdapter
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
                 conversion_options: Optional[Dict[str, Any]] = None):
        """
        Initialize sync orchestrator.

        Args:
            source_dir: Primary source directory
            target_dir: Primary target directory
            source_format: Source format name (e.g., 'claude')
            target_format: Target format name (e.g., 'copilot')
            config_type: Type of config to sync (AGENT, PERMISSION, PROMPT)
            format_registry: Registry containing adapters
            state_manager: State tracking manager
            direction: 'both', 'source-to-target', or 'target-to-source'
            dry_run: If True, don't actually modify files
            force: If True, auto-resolve conflicts using newest file
            verbose: If True, print detailed logs
            conversion_options: Options to pass to adapters (e.g., add_argument_hint)
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
        print()

        # TODO: Implement sync logic
        # pairs = self._discover_file_pairs()
        # for pair in pairs:
        #     action = self._determine_action(pair)
        #     if action == 'conflict': handle conflict
        #     self._execute_sync_action(pair, action)
        # self.state_manager.save()
        # self._print_summary()

        raise NotImplementedError("Sync logic to be implemented")

    def _discover_file_pairs(self) -> List[FilePair]:
        """
        Discover and match files between source and target directories.

        Returns:
            List of FilePair objects representing matched files
        """
        # TODO: Implement file discovery and matching
        raise NotImplementedError("File discovery to be implemented")

    def _determine_action(self, pair: FilePair) -> str:
        """
        Determine what sync action is needed for a file pair.

        Args:
            pair: FilePair to analyze

        Returns:
            Action string: 'source_to_target', 'target_to_source', 'conflict',
                          'delete_target', 'delete_source', or 'skip'
        """
        # TODO: Implement action determination logic
        # Check state manager for last sync
        # Compare modification times
        # Detect conflicts
        raise NotImplementedError("Action determination to be implemented")

    def _resolve_conflict(self, pair: FilePair) -> Optional[str]:
        """
        Resolve sync conflict interactively or automatically.

        Args:
            pair: FilePair with conflict

        Returns:
            Resolved action or None to skip
        """
        # TODO: Implement conflict resolution
        # If force: use newest file
        # Else: prompt user
        raise NotImplementedError("Conflict resolution to be implemented")

    def _execute_sync_action(self, pair: FilePair, action: str):
        """
        Execute sync action for a file pair.

        Args:
            pair: FilePair to sync
            action: Action to execute
        """
        # TODO: Implement sync execution
        # Read source -> to_canonical -> from_canonical -> write target
        # Update state manager
        # Track statistics
        raise NotImplementedError("Sync execution to be implemented")

    def log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(message)
