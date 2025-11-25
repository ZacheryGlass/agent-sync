"""
Cursor AI format adapter.

Cursor stores agents/modes as JSON in:
- Project-level: .cursor/modes.json

File format:
{
  "modes": {
    "agent-name": {
      "name": "Agent Name",
      "description": "Agent description",
      "instructions": "Agent instructions...",
      "tools": {
        "search": true,
        "edit": true,
        "run_commands": true
      },
      "memory": {
        "basic": true,
        "full": false
      },
      "model": "claude-3.5-sonnet"
    }
  }
}

This adapter:
- Parses JSON structure
- Converts boolean tool flags to tool list
- Maps full model names (claude-3.5-sonnet) to canonical (sonnet)
- Preserves Cursor-specific fields (memory settings) in metadata
- Uses instructions field directly (no markdown body separation)

Status: STUB - To be implemented
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, ConfigType


class CursorAdapter(FormatAdapter):
    """
    Adapter for Cursor AI agent format.

    Handles bidirectional conversion between Cursor's modes.json format
    and the canonical agent representation.

    Status: STUB IMPLEMENTATION - Not yet functional
    """

    def __init__(self):
        self.warnings: List[str] = []

    @property
    def format_name(self) -> str:
        return "cursor"

    @property
    def file_extension(self) -> str:
        return ".json"  # Actually modes.json specifically

    @property
    def supported_config_types(self) -> List[ConfigType]:
        # TODO: Cursor might support prompts/rules
        return [ConfigType.AGENT]

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a Cursor modes file."""
        # TODO: Implement - check if file is named 'modes.json' and in .cursor/ dir
        return file_path.name == 'modes.json' and '.cursor' in str(file_path.parent)

    def read(self, file_path: Path, config_type: ConfigType) -> CanonicalAgent:
        """Read Cursor modes file and convert to canonical."""
        # TODO: Implement JSON parsing
        raise NotImplementedError("Cursor adapter not yet implemented")

    def write(self, canonical_obj: CanonicalAgent, file_path: Path, config_type: ConfigType):
        """Write canonical agent to Cursor format file."""
        # TODO: Implement JSON generation
        raise NotImplementedError("Cursor adapter not yet implemented")

    def to_canonical(self, content: str, config_type: ConfigType) -> CanonicalAgent:
        """Convert Cursor format to canonical."""
        # TODO: Implement conversion
        # Parse JSON, extract mode entry, convert tools from booleans to list
        raise NotImplementedError("Cursor adapter not yet implemented")

    def from_canonical(self, canonical_obj: CanonicalAgent, config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """Convert canonical to Cursor format."""
        # TODO: Implement conversion
        # Generate JSON structure with proper nesting
        raise NotImplementedError("Cursor adapter not yet implemented")

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings
