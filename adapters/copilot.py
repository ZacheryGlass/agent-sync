"""
GitHub Copilot format adapter.

GitHub Copilot stores agents as Markdown files with YAML frontmatter in:
- Project-level: .github/agents/

File format:
---
name: agent-name
description: Agent description
tools: ["read", "search", "edit"]  # Array format
model: Claude Sonnet 4|Claude Opus 4  # Full model names
target: vscode
argument-hint: (optional, Copilot-specific)
handoffs: (optional, Copilot-specific)
mcp-servers: (optional, Copilot-specific)
---
Agent instructions in markdown...

This adapter:
- Parses YAML frontmatter + markdown body
- Converts tools from array to list
- Maps full model names (Claude Sonnet 4) to canonical (sonnet)
- Preserves Copilot-specific fields (argument-hint, handoffs, target, mcp-servers) in metadata
- Always adds 'target: vscode' when converting to Copilot format
"""

import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, ConfigType


class CopilotAdapter(FormatAdapter):
    """
    Adapter for GitHub Copilot agent format.

    Handles bidirectional conversion between Copilot's .agent.md format
    and the canonical agent representation.
    """

    # Model name mappings
    MODEL_TO_CANONICAL = {
        'claude sonnet 4': 'sonnet',
        'claude opus 4': 'opus',
        'claude haiku 4': 'haiku',
    }

    MODEL_FROM_CANONICAL = {
        'sonnet': 'Claude Sonnet 4',
        'opus': 'Claude Opus 4',
        'haiku': 'Claude Haiku 4',
    }

    def __init__(self):
        """Initialize adapter with empty warnings list."""
        self.warnings: List[str] = []

    @property
    def format_name(self) -> str:
        return "copilot"

    @property
    def file_extension(self) -> str:
        return ".agent.md"

    @property
    def supported_config_types(self) -> List[ConfigType]:
        # Copilot only supports agents, not permissions or prompts
        return [ConfigType.AGENT]

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a Copilot agent file."""
        return file_path.name.endswith('.agent.md')

    def read(self, file_path: Path, config_type: ConfigType) -> CanonicalAgent:
        """Read Copilot agent file and convert to canonical."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.to_canonical(content, config_type)

    def write(self, canonical_obj: CanonicalAgent, file_path: Path, config_type: ConfigType,
              options: dict = None):
        """Write canonical agent to Copilot format file."""
        content = self.from_canonical(canonical_obj, config_type, options)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def to_canonical(self, content: str, config_type: ConfigType) -> CanonicalAgent:
        """
        Convert Copilot format to canonical.

        Parses YAML frontmatter and markdown body, extracts fields,
        and creates CanonicalAgent with preserved metadata.
        """
        self.warnings = []

        # Parse YAML frontmatter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError("No YAML frontmatter found in Copilot agent file")

        yaml_content, body = match.groups()
        frontmatter = yaml.safe_load(yaml_content)

        # Create canonical agent
        agent = CanonicalAgent(
            name=frontmatter.get('name', ''),
            description=frontmatter.get('description', ''),
            instructions=body.strip(),
            tools=frontmatter.get('tools', []) if isinstance(frontmatter.get('tools'), list) else [],
            model=self._normalize_model(frontmatter.get('model')),
            source_format='copilot'
        )

        # Preserve Copilot-specific fields in metadata
        if 'argument-hint' in frontmatter:
            agent.add_metadata('copilot_argument_hint', frontmatter['argument-hint'])

        if 'handoffs' in frontmatter:
            agent.add_metadata('copilot_handoffs', frontmatter['handoffs'])

        if 'target' in frontmatter:
            agent.add_metadata('copilot_target', frontmatter['target'])

        if 'mcp-servers' in frontmatter:
            agent.add_metadata('copilot_mcp_servers', frontmatter['mcp-servers'])

        return agent

    def from_canonical(self, canonical_obj: CanonicalAgent, config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert canonical to Copilot format.

        Generates YAML frontmatter with Copilot-specific fields and
        markdown body. Options can enable optional fields like argument-hint.
        """
        self.warnings = []
        options = options or {}

        # Build frontmatter
        frontmatter = {
            'name': canonical_obj.name,
            'description': canonical_obj.description,
        }

        # Tools as array
        if canonical_obj.tools:
            frontmatter['tools'] = canonical_obj.tools

        # Model (convert to Copilot full names)
        if canonical_obj.model:
            frontmatter['model'] = self._denormalize_model(canonical_obj.model)

        # Always add target for Copilot
        frontmatter['target'] = canonical_obj.get_metadata('copilot_target', 'vscode')

        # Optional: Add argument-hint if requested or preserved
        if options.get('add_argument_hint') or canonical_obj.get_metadata('copilot_argument_hint'):
            hint = canonical_obj.get_metadata('copilot_argument_hint', canonical_obj.description)
            frontmatter['argument-hint'] = hint

        # Optional: Add handoffs if requested or preserved
        if options.get('add_handoffs') or canonical_obj.get_metadata('copilot_handoffs'):
            frontmatter['handoffs'] = canonical_obj.get_metadata('copilot_handoffs',
                [{'label': 'Next Step', 'agent': 'agent', 'prompt': 'Continue', 'send': False}])

        # MCP servers if preserved
        if canonical_obj.get_metadata('copilot_mcp_servers'):
            frontmatter['mcp-servers'] = canonical_obj.get_metadata('copilot_mcp_servers')

        # Generate YAML
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

        return f"---\n{yaml_str}---\n{canonical_obj.instructions}\n"

    def _normalize_model(self, model: Optional[str]) -> Optional[str]:
        """Convert Copilot model names to canonical form."""
        if not model:
            return None
        return self.MODEL_TO_CANONICAL.get(model.lower(), model.lower())

    def _denormalize_model(self, model: str) -> str:
        """Convert canonical model names to Copilot form."""
        return self.MODEL_FROM_CANONICAL.get(model.lower(), model)

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings
