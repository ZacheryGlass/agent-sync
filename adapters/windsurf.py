"""
Windsurf IDE format adapter.

Windsurf uses a "memories" and "rules" system with markdown files:
- Project-level: .windsurf/memories/ and .windsurf/rules/

File format: Markdown with constitutional framework
```
# Agent Name

Description of agent purpose.

## Rules

NEVER do X
ALWAYS do Y

## Context

Additional context...
```

This adapter:
- Parses markdown structure
- Extracts rules/memories
- Maps to canonical format (may be lossy as Windsurf has unique structure)
- Preserves Windsurf-specific formatting in metadata

Status: STUB - To be implemented
Note: Windsurf's format is less structured than others, may require special handling
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, ConfigType


class WindsurfAdapter(FormatAdapter):
    """
    Adapter for Windsurf IDE agent format.

    Handles bidirectional conversion between Windsurf's memories/rules
    and the canonical agent representation.

    Status: STUB IMPLEMENTATION - Not yet functional
    """

    def __init__(self):
        self.warnings: List[str] = []

    @property
    def format_name(self) -> str:
        return "windsurf"

    @property
    def file_extension(self) -> str:
        return ".md"  # In .windsurf/memories/ or .windsurf/rules/

    @property
    def supported_config_types(self) -> List[ConfigType]:
        # Windsurf has unique "memories" concept that might map to prompts
        return [ConfigType.AGENT]

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a Windsurf memory/rule file."""
        # TODO: Implement - check if file is in .windsurf/ directory
        return '.windsurf' in str(file_path.parent)

    def read(self, file_path: Path, config_type: ConfigType) -> CanonicalAgent:
        """Read Windsurf memory/rule file and convert to canonical."""
        # TODO: Implement markdown parsing with Windsurf structure
        raise NotImplementedError("Windsurf adapter not yet implemented")

    def write(self, canonical_obj: CanonicalAgent, file_path: Path, config_type: ConfigType):
        """Write canonical agent to Windsurf format file."""
        # TODO: Implement markdown generation with Windsurf structure
        raise NotImplementedError("Windsurf adapter not yet implemented")

    def to_canonical(self, content: str, config_type: ConfigType) -> CanonicalAgent:
        """Convert Windsurf format to canonical."""
        # TODO: Implement conversion
        # Parse markdown sections (Rules, Context, etc.)
        raise NotImplementedError("Windsurf adapter not yet implemented")

    def from_canonical(self, canonical_obj: CanonicalAgent, config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """Convert canonical to Windsurf format."""
        # TODO: Implement conversion
        # Generate markdown with Windsurf-specific sections
        raise NotImplementedError("Windsurf adapter not yet implemented")

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings
