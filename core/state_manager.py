"""
Sync state manager for tracking file modification history.

The state manager persists sync history to avoid unnecessary syncs and
enable intelligent change detection. It tracks:
- Last sync time per directory pair
- File modification times at last sync
- Last sync action (which direction)
- Sync metadata (conflicts resolved, errors, etc.)

State is stored in ~/.agent_sync_state.json by default, allowing it to
work across multiple projects and repositories.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class SyncStateManager:
    """
    Manages sync state persistence and retrieval.

    State format:
    {
      "sync_pairs": {
        "/home/user/.claude/agents|/home/user/project/.github/agents": {
          "last_sync": "2025-01-15T10:30:00Z",
          "source_format": "claude",
          "target_format": "copilot",
          "config_type": "agent",
          "files": {
            "planner": {
              "source_mtime": 1705315800.0,
              "target_mtime": 1705315800.0,
              "last_action": "source_to_target",
              "last_sync_time": "2025-01-15T10:30:00Z"
            }
          }
        }
      }
    }

    Usage:
        state_manager = SyncStateManager()
        file_state = state_manager.get_file_state(source_dir, target_dir, 'planner')
        state_manager.update_file_state(source_dir, target_dir, 'planner', ...)
        state_manager.save()
    """

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            state_file: Path to state file (defaults to ~/.agent_sync_state.json)
        """
        self.state_file = state_file or Path.home() / ".agent_sync_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """
        Load sync state from file.

        Returns:
            State dictionary or empty structure if file doesn't exist
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Corrupted state file, start fresh
                return {"sync_pairs": {}}
        return {"sync_pairs": {}}

    def save(self):
        """Save current state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_pair_key(self, source_dir: Path, target_dir: Path) -> str:
        """
        Generate unique key for directory pair.

        Args:
            source_dir: Source directory path
            target_dir: Target directory path

        Returns:
            Unique key string
        """
        return f"{source_dir.resolve()}|{target_dir.resolve()}"

    def get_pair_state(self, source_dir: Path, target_dir: Path) -> Dict:
        """
        Get state for specific sync pair.

        Args:
            source_dir: Source directory
            target_dir: Target directory

        Returns:
            State dictionary for this pair
        """
        key = self.get_pair_key(source_dir, target_dir)
        if key not in self.state["sync_pairs"]:
            self.state["sync_pairs"][key] = {
                "last_sync": None,
                "files": {}
            }
        return self.state["sync_pairs"][key]

    def update_file_state(self,
                         source_dir: Path,
                         target_dir: Path,
                         file_name: str,
                         source_mtime: Optional[float],
                         target_mtime: Optional[float],
                         action: str):
        """
        Update state for a specific file after sync.

        Args:
            source_dir: Source directory
            target_dir: Target directory
            file_name: Base name of file (without extension)
            source_mtime: Source file modification time
            target_mtime: Target file modification time
            action: Sync action performed (source_to_target, target_to_source, etc.)
        """
        pair_state = self.get_pair_state(source_dir, target_dir)
        pair_state["files"][file_name] = {
            "source_mtime": source_mtime,
            "target_mtime": target_mtime,
            "last_action": action,
            "last_sync_time": datetime.now().isoformat()
        }
        pair_state["last_sync"] = datetime.now().isoformat()

    def get_file_state(self,
                      source_dir: Path,
                      target_dir: Path,
                      file_name: str) -> Optional[Dict]:
        """
        Get state for a specific file.

        Args:
            source_dir: Source directory
            target_dir: Target directory
            file_name: Base name of file

        Returns:
            File state dict or None if no previous sync
        """
        pair_state = self.get_pair_state(source_dir, target_dir)
        return pair_state["files"].get(file_name)

    def remove_file_state(self,
                         source_dir: Path,
                         target_dir: Path,
                         file_name: str):
        """
        Remove state for a specific file (e.g., after deletion).

        Args:
            source_dir: Source directory
            target_dir: Target directory
            file_name: Base name of file to remove
        """
        pair_state = self.get_pair_state(source_dir, target_dir)
        if file_name in pair_state["files"]:
            del pair_state["files"][file_name]

    def clear_pair_state(self, source_dir: Path, target_dir: Path):
        """
        Clear all state for a directory pair.

        Args:
            source_dir: Source directory
            target_dir: Target directory
        """
        key = self.get_pair_key(source_dir, target_dir)
        if key in self.state["sync_pairs"]:
            del self.state["sync_pairs"][key]
