"""
Claude Code format adapter - coordinator.

Delegates to config-type-specific handlers.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, CanonicalPermission, CanonicalSlashCommand, ConfigType
from .handlers.agent_handler import ClaudeAgentHandler
from .handlers.perm_handler import ClaudePermissionHandler
from .handlers.slash_command_handler import ClaudeSlashCommandHandler


class ClaudeAdapter(FormatAdapter):
    """
    Adapter for Claude Code format.

    Coordinates between different config type handlers.
    """

    def __init__(self):
        """Initialize adapter with handlers for each config type."""
        self.warnings: List[str] = []
        self._handlers = {
            ConfigType.AGENT: ClaudeAgentHandler(),
            ConfigType.PERMISSION: ClaudePermissionHandler(),
            ConfigType.SLASH_COMMAND: ClaudeSlashCommandHandler()
        }

    @property
    def format_name(self) -> str:
        return "claude"

    @property
    def file_extension(self) -> str:
        return ".md"

    def get_file_extension(self, config_type: ConfigType) -> str:
        """Claude uses .json for permissions (settings.json) and .md for agents."""
        if config_type == ConfigType.PERMISSION:
            return ".json"
        return self.file_extension

    @property
    def supported_config_types(self) -> List[ConfigType]:
        return list(self._handlers.keys())

    def can_handle(self, file_path: Path) -> bool:
        """
        Check if file is a Claude agent file or settings file.

        Claude agents are .md files that are NOT .agent.md files.
        Settings are settings.json or settings.local.json.
        """
        if file_path.name in ('settings.json', 'settings.local.json'):
            return True
        return (file_path.suffix == '.md' and
                not file_path.name.endswith('.agent.md'))

    def read(self, file_path: Path, config_type: ConfigType) -> Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand]:
        """Read file and convert to canonical."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        canonical = self.to_canonical(content, config_type)

        # Post-processing: set name from filename for slash commands if missing
        if config_type == ConfigType.SLASH_COMMAND and hasattr(canonical, 'name') and not canonical.name:
            canonical.name = file_path.stem

        return canonical

    def write(self, canonical_obj: Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand],
              file_path: Path, config_type: ConfigType, options: dict = None):
        """Write canonical to file in Claude format."""
        content = self.from_canonical(canonical_obj, config_type, options)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def to_canonical(self, content: str, config_type: ConfigType) -> Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand]:
        """Convert Claude format to canonical (delegates to handler)."""
        self.warnings = []
        handler = self._get_handler(config_type)
        return handler.to_canonical(content)

    def from_canonical(self, canonical_obj: Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand],
                      config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """Convert canonical to Claude format (delegates to handler)."""
        self.warnings = []
        handler = self._get_handler(config_type)
        return handler.from_canonical(canonical_obj, options)

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings

    def _get_handler(self, config_type: ConfigType):
        """Get handler for config type."""
        if config_type not in self._handlers:
            raise ValueError(f"Unsupported config type: {config_type}")
        return self._handlers[config_type]

    # Delegation methods for backward compatibility with tests
    def _parse_tools(self, tools_value):
        """Delegate to agent handler for backward compatibility."""
        return self._handlers[ConfigType.AGENT]._parse_tools(tools_value)

    def _normalize_model(self, model: Optional[str]) -> Optional[str]:
        """Delegate to agent handler for backward compatibility."""
        return self._handlers[ConfigType.AGENT]._normalize_model(model)
