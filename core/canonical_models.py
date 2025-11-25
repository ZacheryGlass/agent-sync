"""
Canonical data models for universal configuration representation.

This module defines the "lingua franca" data structures that all format-specific
adapters convert to/from. This hub-and-spoke approach allows N formats to be
supported with 2N converters instead of N² converters.

Design principles:
- Core fields: Common to ALL formats (name, description, etc.)
- Metadata dict: Preserves format-specific fields for round-trip fidelity
- Source tracking: Helps with intelligent conversion decisions
- Version tracking: Enables schema evolution

Each config type (agents, permissions, prompts) gets its own canonical model.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ConfigType(Enum):
    """Types of configuration that can be synced."""
    AGENT = "agent"
    PERMISSION = "permission"
    PROMPT = "prompt"


@dataclass
class CanonicalAgent:
    """
    Canonical representation of an AI agent configuration.

    This is the universal format that all agent formats (Claude .md, Copilot .agent.md,
    Cursor .json, etc.) convert to and from.

    Attributes:
        name: Agent identifier (used for file matching)
        description: Human-readable description of agent purpose
        instructions: Full markdown instructions/system prompt
        tools: List of available tools (normalized names)
        model: Model identifier in canonical form (sonnet, opus, haiku, etc.)
        metadata: Format-specific fields preserved for round-trip conversion
        source_format: Which format this was originally parsed from
        version: Schema version for future compatibility
    """
    # Core fields (supported by all formats)
    name: str
    description: str
    instructions: str  # Markdown body content

    # Tools/capabilities
    tools: List[str] = field(default_factory=list)

    # Model configuration (normalized to canonical names)
    model: Optional[str] = None

    # Extended attributes (format-specific, preserved for round-trips)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    source_format: Optional[str] = None
    version: str = "1.0"

    def add_metadata(self, key: str, value: Any):
        """
        Store format-specific field that may not have equivalents in other formats.

        Example: Copilot's 'handoffs' feature doesn't exist in Claude, so we store
        it in metadata to preserve it if we do a round-trip conversion.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        """Retrieve format-specific metadata with optional default."""
        return self.metadata.get(key, default)

    def has_metadata(self, key: str) -> bool:
        """Check if metadata key exists."""
        return key in self.metadata


@dataclass
class CanonicalPermission:
    """
    Canonical representation of permission/security configuration.

    Different tools handle permissions differently:
    - Claude: permissionMode in agents, or settings.json
    - Copilot: Doesn't have explicit permission model
    - Cursor: Privacy settings, allowed directories

    Attributes:
        allow: List of explicitly allowed operations/paths
        deny: List of explicitly denied operations/paths
        ask: List of operations that require user confirmation
        default_mode: Default permission behavior (allow, deny, ask)
        metadata: Format-specific permission settings
        source_format: Original format
    """
    allow: List[str] = field(default_factory=list)
    deny: List[str] = field(default_factory=list)
    ask: List[str] = field(default_factory=list)
    default_mode: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_format: Optional[str] = None
    version: str = "1.0"


@dataclass
class CanonicalPrompt:
    """
    Canonical representation of a saved prompt/snippet.

    Some tools allow saving reusable prompts/snippets:
    - Claude: Saved prompts
    - Copilot: Not directly supported
    - Cursor: Composer rules

    Attributes:
        name: Prompt identifier
        content: The actual prompt text
        description: What this prompt does
        category: Optional categorization (debugging, refactoring, etc.)
        tags: Optional tags for filtering
        metadata: Format-specific fields
        source_format: Original format
    """
    name: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_format: Optional[str] = None
    version: str = "1.0"
