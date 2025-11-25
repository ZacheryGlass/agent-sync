"""
Format adapters for converting between tool-specific formats and canonical representation.

This module contains concrete implementations of FormatAdapter for each supported
AI coding tool. Each adapter knows how to:
- Parse the tool's configuration format
- Convert to canonical representation
- Convert from canonical back to tool format
- Preserve format-specific fields via metadata

Available adapters:
- ClaudeAdapter: Claude Code (.md files)
- CopilotAdapter: GitHub Copilot (.agent.md files)
- CursorAdapter: Cursor AI (.cursor/modes.json)
- WindsurfAdapter: Windsurf IDE (memories/rules)
- ContinueAdapter: Continue.dev (config.yaml)

Adding a new adapter:
1. Create new file (e.g., myagent.py)
2. Implement FormatAdapter interface
3. Register with FormatRegistry in your application
"""

from .claude import ClaudeAdapter
from .copilot import CopilotAdapter
from .cursor import CursorAdapter
from .windsurf import WindsurfAdapter
from .continue_dev import ContinueAdapter

__all__ = [
    'ClaudeAdapter',
    'CopilotAdapter',
    'CursorAdapter',
    'WindsurfAdapter',
    'ContinueAdapter',
]
