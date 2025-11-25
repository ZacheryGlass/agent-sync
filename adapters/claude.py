"""
Claude Code format adapter.

Claude Code stores agents as Markdown files with YAML frontmatter in:
- User-level: ~/.claude/agents/
- Project-level: .claude/agents/

File format:
---
name: agent-name
description: Agent description
tools: Read, Grep, Glob, Bash  # Comma-separated string
model: sonnet|opus|haiku|inherit
permissionMode: (optional, Claude-specific)
skills: (optional, Claude-specific)
---
Agent instructions in markdown...

This adapter:
- Parses YAML frontmatter + markdown body
- Normalizes tools from comma-separated string to list
- Preserves Claude-specific fields (permissionMode, skills) in metadata
- Uses short model names (sonnet, opus, haiku) as canonical form
"""

import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, ConfigType


class ClaudeAdapter(FormatAdapter):
    """
    Adapter for Claude Code agent format.

    Handles bidirectional conversion between Claude's .md format and
    the canonical agent representation.
    """

    def __init__(self):
        """Initialize adapter with empty warnings list."""
        self.warnings: List[str] = []

    @property
    def format_name(self) -> str:
        return "claude"

    @property
    def file_extension(self) -> str:
        return ".md"

    @property
    def supported_config_types(self) -> List[ConfigType]:
        # TODO: Add ConfigType.PERMISSION when implementing settings.json support
        return [ConfigType.AGENT]

    def can_handle(self, file_path: Path) -> bool:
        """
        Check if file is a Claude agent file.

        Claude agents are .md files that are NOT .agent.md files.
        """
        return (file_path.suffix == '.md' and
                not file_path.name.endswith('.agent.md'))

    def read(self, file_path: Path, config_type: ConfigType) -> CanonicalAgent:
        """Read Claude agent file and convert to canonical."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.to_canonical(content, config_type)

    def write(self, canonical_obj: CanonicalAgent, file_path: Path, config_type: ConfigType):
        """Write canonical agent to Claude format file."""
        content = self.from_canonical(canonical_obj, config_type)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def to_canonical(self, content: str, config_type: ConfigType) -> CanonicalAgent:
        """
        Convert Claude format to canonical.

        Parses YAML frontmatter and markdown body, extracts fields,
        and creates CanonicalAgent with preserved metadata.
        """
        self.warnings = []

        # Parse YAML frontmatter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError("No YAML frontmatter found in Claude agent file")

        yaml_content, body = match.groups()
        frontmatter = yaml.safe_load(yaml_content)

        # Create canonical agent
        agent = CanonicalAgent(
            name=frontmatter.get('name', ''),
            description=frontmatter.get('description', ''),
            instructions=body.strip(),
            tools=self._parse_tools(frontmatter.get('tools', '')),
            model=self._normalize_model(frontmatter.get('model')),
            source_format='claude'
        )

        # Preserve Claude-specific fields in metadata
        if 'permissionMode' in frontmatter:
            agent.add_metadata('claude_permission_mode', frontmatter['permissionMode'])

        if 'skills' in frontmatter:
            agent.add_metadata('claude_skills', frontmatter['skills'])

        return agent

    def from_canonical(self, canonical_obj: CanonicalAgent, config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert canonical to Claude format.

        Generates YAML frontmatter with Claude-specific fields and
        markdown body.
        """
        self.warnings = []
        options = options or {}

        # Build frontmatter
        frontmatter = {
            'name': canonical_obj.name,
            'description': canonical_obj.description,
        }

        # Tools as comma-separated string
        if canonical_obj.tools:
            frontmatter['tools'] = ', '.join(canonical_obj.tools)

        # Model
        if canonical_obj.model:
            frontmatter['model'] = canonical_obj.model

        # Restore Claude-specific metadata
        if canonical_obj.get_metadata('claude_permission_mode'):
            frontmatter['permissionMode'] = canonical_obj.get_metadata('claude_permission_mode')

        if canonical_obj.get_metadata('claude_skills'):
            frontmatter['skills'] = canonical_obj.get_metadata('claude_skills')

        # Generate YAML
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

        return f"---\n{yaml_str}---\n{canonical_obj.instructions}\n"

    def _parse_tools(self, tools_value: Any) -> List[str]:
        """
        Parse tools from comma-separated string or list.

        Args:
            tools_value: Either string "tool1, tool2" or list ["tool1", "tool2"]

        Returns:
            List of tool names
        """
        if isinstance(tools_value, str):
            return [t.strip() for t in tools_value.split(',') if t.strip()]
        elif isinstance(tools_value, list):
            return tools_value
        return []

    def _normalize_model(self, model: Optional[str]) -> Optional[str]:
        """
        Normalize model name to canonical form.

        Claude already uses short names (sonnet, opus, haiku) which
        are the canonical form, so just lowercase and return.
        """
        if not model:
            return None
        return model.lower()

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings
