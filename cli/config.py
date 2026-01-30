"""
Configuration file handling for agent-sync CLI.

This module provides functionality to read and write configuration files
for the agent-sync tool, enabling a config-first workflow where users
can save their preferences and avoid repetitive CLI flags.

Configuration file location: ~/.agent-sync.toml
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w


DEFAULT_CONFIG_PATH = Path.home() / ".agent-sync.toml"


class Config:
    """
    Configuration for agent-sync CLI.
    
    Attributes:
        source_dir: Source directory path
        target_dir: Target directory path
        source_format: Source format name
        target_format: Target format name
        state_file: Custom state file path
        dry_run: Enable dry-run mode by default
        verbose: Enable verbose output by default
        force: Auto-resolve conflicts by default
        strict: Enable strict mode by default
        yes: Skip confirmation prompts by default
        only: Default config types to sync
        direction: Default sync direction
        add_argument_hint: Add argument-hint field by default
        add_handoffs: Add handoffs placeholder by default
        no_autodiscover: Disable auto-discovery by default
    """
    
    def __init__(self, **kwargs):
        """Initialize config with optional values."""
        # Core paths and formats
        self.source_dir: Optional[str] = kwargs.get('source_dir')
        self.target_dir: Optional[str] = kwargs.get('target_dir')
        self.source_format: Optional[str] = kwargs.get('source_format')
        self.target_format: Optional[str] = kwargs.get('target_format')
        
        # Optional settings
        self.state_file: Optional[str] = kwargs.get('state_file')
        self.dry_run: bool = kwargs.get('dry_run', False)
        self.verbose: bool = kwargs.get('verbose', False)
        self.force: bool = kwargs.get('force', False)
        self.strict: bool = kwargs.get('strict', False)
        self.yes: bool = kwargs.get('yes', False)
        self.only: Optional[str] = kwargs.get('only')
        self.direction: str = kwargs.get('direction', 'both')
        self.add_argument_hint: bool = kwargs.get('add_argument_hint', False)
        self.add_handoffs: bool = kwargs.get('add_handoffs', False)
        self.no_autodiscover: bool = kwargs.get('no_autodiscover', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for TOML serialization."""
        data = {}
        
        # Only include non-None values
        if self.source_dir:
            data['source_dir'] = self.source_dir
        if self.target_dir:
            data['target_dir'] = self.target_dir
        if self.source_format:
            data['source_format'] = self.source_format
        if self.target_format:
            data['target_format'] = self.target_format
        
        # Optional settings (only if non-default)
        if self.state_file:
            data['state_file'] = self.state_file
        if self.dry_run:
            data['dry_run'] = True
        if self.verbose:
            data['verbose'] = True
        if self.force:
            data['force'] = True
        if self.strict:
            data['strict'] = True
        if self.yes:
            data['yes'] = True
        if self.only:
            data['only'] = self.only
        if self.direction != 'both':
            data['direction'] = self.direction
        if self.add_argument_hint:
            data['add_argument_hint'] = True
        if self.add_handoffs:
            data['add_handoffs'] = True
        if self.no_autodiscover:
            data['no_autodiscover'] = True
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        return cls(**data)


def load_config(config_path: Optional[Path] = None) -> Optional[Config]:
    """
    Load configuration from TOML file.
    
    Args:
        config_path: Path to config file (defaults to ~/.agent-sync.toml)
    
    Returns:
        Config object if file exists, None otherwise
    
    Raises:
        ValueError: If config file is malformed
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'rb') as f:
            data = tomllib.load(f)
        return Config.from_dict(data)
    except Exception as e:
        raise ValueError(f"Failed to load config from {config_path}: {e}")


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to TOML file.
    
    Args:
        config: Config object to save
        config_path: Path to config file (defaults to ~/.agent-sync.toml)
    
    Raises:
        OSError: If file cannot be written
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict and write
    data = config.to_dict()
    with open(config_path, 'wb') as f:
        tomli_w.dump(data, f)


def validate_config(config: Config, registry) -> list[str]:
    """
    Validate configuration values.
    
    Args:
        config: Config object to validate
        registry: FormatRegistry to validate format names
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Validate formats if specified
    if config.source_format and not registry.get_adapter(config.source_format):
        errors.append(f"Invalid source format: {config.source_format}")
    
    if config.target_format and not registry.get_adapter(config.target_format):
        errors.append(f"Invalid target format: {config.target_format}")
    
    # Validate paths if specified
    if config.source_dir:
        path = Path(config.source_dir).expanduser()
        if not path.exists():
            errors.append(f"Source directory does not exist: {config.source_dir}")
        elif not path.is_dir():
            errors.append(f"Source path is not a directory: {config.source_dir}")
    
    if config.target_dir:
        path = Path(config.target_dir).expanduser()
        # Target dir doesn't need to exist but parent should
        if path.exists() and not path.is_dir():
            errors.append(f"Target path exists but is not a directory: {config.target_dir}")
    
    # Validate direction
    if config.direction not in ['both', 'source-to-target', 'target-to-source']:
        errors.append(f"Invalid direction: {config.direction}")
    
    return errors
