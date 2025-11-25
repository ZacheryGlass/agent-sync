# Plugin Development Guide

This directory is reserved for third-party format adapters. You can create custom adapters for AI coding tools not officially supported by this project.

## Creating a Plugin

### 1. Create Your Adapter File

Create a new Python file in this directory (e.g., `myagent.py`):

```python
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.adapter_interface import FormatAdapter
from core.canonical_models import CanonicalAgent, ConfigType


class MyAgentAdapter(FormatAdapter):
    """Adapter for MyAgent AI tool."""

    def __init__(self):
        self.warnings: List[str] = []

    @property
    def format_name(self) -> str:
        return "myagent"

    @property
    def file_extension(self) -> str:
        return ".myagent"

    @property
    def supported_config_types(self) -> List[ConfigType]:
        return [ConfigType.AGENT]

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix == '.myagent'

    def read(self, file_path: Path, config_type: ConfigType) -> CanonicalAgent:
        with open(file_path, 'r') as f:
            content = f.read()
        return self.to_canonical(content, config_type)

    def write(self, canonical_obj: CanonicalAgent, file_path: Path, config_type: ConfigType):
        content = self.from_canonical(canonical_obj, config_type)
        with open(file_path, 'w') as f:
            f.write(content)

    def to_canonical(self, content: str, config_type: ConfigType) -> CanonicalAgent:
        # Parse your format and convert to CanonicalAgent
        # ...
        pass

    def from_canonical(self, canonical_obj: CanonicalAgent, config_type: ConfigType,
                      options: Optional[Dict[str, Any]] = None) -> str:
        # Convert CanonicalAgent to your format
        # ...
        pass

    def get_conversion_warnings(self) -> List[str]:
        return self.warnings
```

### 2. Register Your Adapter

In your application code:

```python
from core.registry import FormatRegistry
from plugins.myagent import MyAgentAdapter

registry = FormatRegistry()
registry.register(MyAgentAdapter())
```

### 3. Test Your Adapter

Create test files in `tests/fixtures/myagent/` and write unit tests.

## Guidelines

### Field Mapping

Map your format's fields to canonical fields:
- **name**: Agent identifier
- **description**: Purpose/description
- **instructions**: Full instructions/prompt
- **tools**: List of available tools
- **model**: Model identifier

### Preserving Format-Specific Fields

Use metadata to preserve fields unique to your format:

```python
# When converting TO canonical
agent.add_metadata('myagent_special_field', value)

# When converting FROM canonical
if canonical_obj.get_metadata('myagent_special_field'):
    # Restore the field
    pass
```

This enables lossless round-trip conversions.

### Model Name Normalization

Convert your tool's model names to canonical form:
- `sonnet` - Claude Sonnet 4.5
- `opus` - Claude Opus 4.5
- `haiku` - Claude Haiku 4.5

Maintain a mapping dictionary:
```python
MODEL_TO_CANONICAL = {
    'my-sonnet-4': 'sonnet',
    'my-opus-4': 'opus',
}
```

### Error Handling

Raise descriptive errors:
```python
if not valid:
    raise ValueError(f"Invalid {self.format_name} format: {reason}")
```

### Warnings

Collect warnings for dropped/lossy conversions:
```python
if 'unsupported_field' in data:
    self.warnings.append(f"Dropped unsupported field: {field}")
```

## Example Plugins

See the built-in adapters for examples:
- `adapters/claude.py` - YAML frontmatter + markdown
- `adapters/copilot.py` - YAML frontmatter + markdown with arrays
- `adapters/cursor.py` - JSON structure (stub)

## Plugin Discovery (Coming Soon)

Future versions will support automatic plugin discovery:
- Drop plugin file in `plugins/` directory
- Plugin is automatically loaded and registered
- No code changes needed

## Sharing Your Plugin

Consider sharing your adapter:
1. Create a GitHub repository
2. Package as Python module
3. Submit PR to add to official adapters if widely used

## Support

For questions:
- Check `core/adapter_interface.py` for full interface documentation
- Look at existing adapters for examples
- Open an issue on GitHub
