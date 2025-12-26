"""
Copilot slash command (prompt file) config type handler.

Handles conversion of slash command configurations between Copilot format
and canonical representation.
"""

from typing import Any, Dict, Optional
from core.canonical_models import CanonicalSlashCommand, ConfigType
from adapters.shared.config_type_handler import ConfigTypeHandler
from adapters.shared.frontmatter import parse_yaml_frontmatter, build_yaml_frontmatter


class CopilotSlashCommandHandler(ConfigTypeHandler):
    """Handler for Copilot prompt files (.prompt.md)."""

    @property
    def config_type(self) -> ConfigType:
        return ConfigType.SLASH_COMMAND

    def to_canonical(self, content: str) -> CanonicalSlashCommand:
        """
        Convert Copilot prompt file to canonical.
        """
        frontmatter, body = parse_yaml_frontmatter(content)

        # Create canonical slash command
        cmd = CanonicalSlashCommand(
            name=frontmatter.get('name', ''),
            description=frontmatter.get('description', ''),
            instructions=body,
            argument_hint=frontmatter.get('argument-hint'),
            model=frontmatter.get('model'),
            allowed_tools=frontmatter.get('tools'),
            source_format='copilot'
        )

        # Preserve Copilot-specific fields in metadata
        if 'agent' in frontmatter:
            cmd.add_metadata('copilot_agent', frontmatter['agent'])

        return cmd

    def from_canonical(self, canonical_obj: Any,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert canonical slash command to Copilot format.
        """
        if not isinstance(canonical_obj, CanonicalSlashCommand):
            raise ValueError("Expected CanonicalSlashCommand")

        options = options or {}

        # Build frontmatter
        frontmatter = {
            'name': canonical_obj.name,
            'description': canonical_obj.description,
        }

        if canonical_obj.argument_hint:
            frontmatter['argument-hint'] = canonical_obj.argument_hint
            
        if canonical_obj.model:
            frontmatter['model'] = canonical_obj.model
            
        if canonical_obj.allowed_tools:
            frontmatter['tools'] = canonical_obj.allowed_tools
            
        if canonical_obj.get_metadata('copilot_agent'):
            frontmatter['agent'] = canonical_obj.get_metadata('copilot_agent')

        return build_yaml_frontmatter(frontmatter, canonical_obj.instructions)
