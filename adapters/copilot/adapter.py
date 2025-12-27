"""
GitHub Copilot format adapter - coordinator.

Delegates to config-type-specific handlers.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, CanonicalPermission, CanonicalSlashCommand, ConfigType
from .handlers.agent_handler import CopilotAgentHandler
from .handlers.perm_handler import CopilotPermissionHandler
from .handlers.slash_command_handler import CopilotSlashCommandHandler


class CopilotAdapter(FormatAdapter):
    """
    Adapter for GitHub Copilot format.

    Coordinates between different config type handlers.
    """

    def __init__(self):
        """Initialize adapter with handlers."""
        self.warnings: List[str] = []
        self._handlers = {
            ConfigType.AGENT: CopilotAgentHandler(),
            ConfigType.PERMISSION: CopilotPermissionHandler(),
            ConfigType.SLASH_COMMAND: CopilotSlashCommandHandler()
        }

    @property
    def format_name(self) -> str:
        return "copilot"

    @property
    def file_extension(self) -> str:
        return ".agent.md"

    def get_file_extension(self, config_type: ConfigType) -> str:
        """Copilot uses .perm.json for permissions, .prompt.md for prompts, and .agent.md for agents."""
        if config_type == ConfigType.PERMISSION:
            return ".perm.json"
        if config_type == ConfigType.SLASH_COMMAND:
            return ".prompt.md"
        return self.file_extension

    @property
    def supported_config_types(self) -> List[ConfigType]:
        return list(self._handlers.keys())

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a Copilot agent file, permission file, or prompt file."""
        return (file_path.name.endswith('.agent.md') or
                file_path.name.endswith('.perm.json') or
                file_path.name.endswith('.prompt.md'))

    def read(self, file_path: Path, config_type: ConfigType) -> Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand]:
        """Read file and convert to canonical."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.to_canonical(content, config_type)

    def write(self, canonical_obj: Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand],
              file_path: Path,
              config_type: ConfigType, options: dict = None):
        """Write canonical to file in Copilot format."""
        content = self.from_canonical(canonical_obj, config_type, options)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def to_canonical(self, content: str, config_type: ConfigType) -> Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand]:
        """Convert Copilot format to canonical (delegates to handler)."""
        self.warnings = []
        handler = self._get_handler(config_type)
        return handler.to_canonical(content)

    def from_canonical(self, canonical_obj: Union[CanonicalAgent, CanonicalPermission, CanonicalSlashCommand], config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """Convert canonical to Copilot format (delegates to handler)."""
        self.warnings = []
        handler = self._get_handler(config_type)
        return handler.from_canonical(canonical_obj, options)

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings

    def clear_conversion_warnings(self):
        self.warnings = []

    def _get_handler(self, config_type: ConfigType):
        """Get handler for config type."""
        if config_type not in self._handlers:
            raise ValueError(f"Unsupported config type: {config_type}")
        return self._handlers[config_type]

    # Delegation methods for backward compatibility with tests
    def _normalize_model(self, model: Optional[str]) -> Optional[str]:
        """Delegate to agent handler for backward compatibility."""
        return self._handlers[ConfigType.AGENT]._normalize_model(model)

    def _denormalize_model(self, model: str) -> str:
        """Delegate to agent handler for backward compatibility."""
        return self._handlers[ConfigType.AGENT]._denormalize_model(model)
