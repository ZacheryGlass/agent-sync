# Architecture Overview

This document provides a high-level overview of the universal agent sync architecture.

## Design Philosophy

### Problem
The original implementation only supported Claude Code ↔ GitHub Copilot sync. Adding a third format (Codex) would require writing 4 new conversion functions (Claude→Codex, Codex→Claude, Copilot→Codex, Codex→Copilot). For N formats, this scales as N² converters.

### Solution
**Hub-and-Spoke with Canonical Data Model**

Instead of direct format-to-format conversions, we use an intermediate "canonical" representation:

```
Claude → Canonical ← Copilot
           ↓
        Codex
```

For N formats, we need only 2N converters (one to canonical, one from canonical).

**Scaling comparison:**
- 6 formats with direct conversion: 30 converters needed
- 6 formats with canonical model: 12 converters needed (60% reduction)

## Core Components

### 1. Canonical Models (`core/canonical_models.py`)

Universal data structures that all formats convert to/from:

- **CanonicalAgent**: Universal agent representation
  - Core fields: name, description, instructions, tools, model
  - Metadata dict: Preserves format-specific fields

- **CanonicalPermission**: Universal permission settings
- **CanonicalPrompt**: Universal saved prompt

**Why metadata?**
Format-specific fields (like Copilot's `handoffs` or Claude's `permissionMode`) are stored in metadata to enable lossless round-trip conversions.

### 2. Format Adapter Interface (`core/adapter_interface.py`)

Abstract base class defining the contract for all format converters:

```python
class FormatAdapter(ABC):
    def to_canonical(self, content: str) -> CanonicalAgent
    def from_canonical(self, agent: CanonicalAgent) -> str
```

Each AI tool implements this interface once. Benefits:
- Uniform interface for all formats
- Easy to add new formats
- Testable in isolation

### 3. Format Registry (`core/registry.py`)

Central directory of available adapters:

- Registers adapters by name
- Auto-detects format from file paths
- Validates format support for config types

### 4. Sync Orchestrator (`core/orchestrator.py`)

Coordinates sync operations:

- File discovery and matching
- Change detection via state manager
- Conflict resolution (interactive or automatic)
- Format conversion via adapters
- Statistics tracking

### 5. State Manager (`core/state_manager.py`)

Tracks sync history to enable intelligent change detection:

- Stores file modification times
- Tracks last sync action
- Prevents unnecessary syncs
- Persists to `~/.agent_sync_state.json`

## Data Flow

### Sync Operation Flow

```
1. Orchestrator discovers file pairs
   └─> Uses registry to detect formats

2. For each pair, determine action needed
   └─> Check state manager for changes
   └─> Detect conflicts

3. Execute conversion
   Source File → Source Adapter.read()
              → to_canonical()
              → CanonicalAgent
              → from_canonical()
              → Target Adapter.write()
              → Target File

4. Update state manager
   └─> Record modification times
   └─> Save action taken
```

### Conversion Flow

```
Format-Specific → Parse → Normalize → Canonical
                                          ↓
Canonical → Denormalize → Serialize → Format-Specific
```

Each adapter handles:
- **Parsing**: Extract data from format's structure (YAML, JSON, etc.)
- **Normalization**: Convert to canonical field names/types
- **Model mapping**: Translate model names (e.g., "Claude Sonnet 4" → "sonnet")
- **Tool conversion**: Unify tool representations
- **Metadata preservation**: Store unique fields for round-trips

### Handler-Based Adapter Architecture

Each format adapter uses a handler-based pattern to separate concerns by config type:

```
FormatAdapter (Coordinator)
    ├── AgentHandler (handles AGENT config type)
    ├── PermissionHandler (handles PERMISSION config type)
    └── PromptHandler (handles PROMPT config type)
```

**Benefits:**
- **Single Responsibility**: Each handler focuses on one config type
- **Scalability**: Easy to add new config types without bloating adapter files
- **Testability**: Handlers can be tested in isolation
- **Reusability**: Shared utilities (frontmatter parsing) reduce duplication
- **Maintainability**: Smaller, focused files instead of large monolithic adapters

**Structure:**
```
adapters/
├── shared/
│   ├── config_type_handler.py    # Handler interface
│   └── frontmatter.py             # Shared YAML parsing utilities
├── claude/
│   ├── adapter.py                 # Coordinator (delegates to handlers)
│   └── handlers/
│       ├── agent_handler.py       # AGENT config type logic
│       └── perm_handler.py        # PERMISSION config type logic
└── copilot/
    ├── adapter.py                 # Coordinator
    └── handlers/
        └── agent_handler.py       # AGENT config type logic
```

**Coordinator Pattern**: The adapter class (e.g., ClaudeAdapter) registers handlers in `__init__()` and delegates `to_canonical()` and `from_canonical()` calls to the appropriate handler based on config type.

**Handler Interface**: All handlers extend `ConfigTypeHandler` and implement:
- `config_type` property: Returns the ConfigType this handler processes
- `to_canonical(content)`: Convert format content to canonical model
- `from_canonical(canonical_obj, options)`: Convert canonical model to format content

**Shared Utilities**:
- `adapters/shared/frontmatter.py`: Provides `parse_yaml_frontmatter()` and `build_yaml_frontmatter()` for formats using YAML frontmatter + Markdown (Claude, Copilot)
- Eliminates code duplication across adapters

## Format Adapters

### Implemented Adapters

**ClaudeAdapter** (`adapters/claude/`)
- Format: YAML frontmatter + Markdown
- File: `agent-name.md` (agents), `settings.json` (permissions)
- Tools: Comma-separated string
- Model: Short names (sonnet, opus, haiku)
- Unique fields: permissionMode, skills
- Handlers: `ClaudeAgentHandler`, `ClaudePermissionHandler`

**CopilotAdapter** (`adapters/copilot/`)
- Format: YAML frontmatter + Markdown
- File: `agent-name.agent.md`
- Tools: Array
- Model: Full names (Claude Sonnet 4)
- Unique fields: argument-hint, handoffs, target, mcp-servers
- Handlers: `CopilotAgentHandler`

### Adding New Adapters

Use `adapters/example/` as a template for implementing new format adapters.

**Steps:**
1. Copy `adapters/example/` directory to `adapters/yourformat/`
2. In `adapters/yourformat/adapter.py`:
   - Rename `ExampleAdapter` to `YourFormatAdapter`
   - Update `format_name`, `file_extension`, and `can_handle()` for your format
   - Add handlers in `__init__()` for each config type you support
3. In `adapters/yourformat/handlers/agent_handler.py`:
   - Rename `ExampleAgentHandler` to `YourFormatAgentHandler`
   - Implement `to_canonical()` to parse your format
   - Implement `from_canonical()` to serialize to your format
   - Use shared utilities (`parse_yaml_frontmatter()`, etc.) where applicable
4. Add more handlers for additional config types (permissions, prompts, etc.)
5. Register your adapter in `cli/main.py` or your application

See `ClaudeAdapter` and `CopilotAdapter` for working examples of the handler-based pattern.

## Information Preservation

### Lossless Round-Trips

The metadata dictionary enables lossless round-trip conversions:

```
Claude → Canonical (stores permissionMode in metadata)
       → Copilot (drops permissionMode, stores in metadata)
       → Canonical (retrieves from metadata)
       → Claude (restores permissionMode)
```

### Lossy Conversions

Some conversions are inherently lossy:
- Tool lists may have different granularities
- Model names may not map 1:1
- Format-specific features may not have equivalents

Adapters collect warnings during conversion to inform users.

## Extensibility

### Adding New Config Types

1. Define canonical model in `canonical_models.py`
2. Add to `ConfigType` enum
3. Implement adapter methods for new type
4. Update orchestrator to handle new type

Example: Adding permission sync
```python
@dataclass
class CanonicalPermission:
    allow: List[str]
    deny: List[str]
    default_mode: str
```

### Adding New Formats

1. Create adapter class
2. Implement `FormatAdapter` interface
3. Register with registry
4. Add tests and fixtures

Complexity: O(1) - only need to implement 2 methods (to/from canonical)

## Testing Strategy

### Unit Tests
- Canonical models: Field manipulation, metadata
- Adapters: Parsing, serialization, round-trips
- Registry: Registration, detection, queries
- Orchestrator: File discovery, action determination
- State manager: Persistence, retrieval

### Integration Tests
- End-to-end sync operations
- Multi-format conversions
- Conflict resolution
- State persistence across syncs

See `tests/` directory for test structure.

## Design Patterns Used

1. **Adapter Pattern**: Convert between incompatible interfaces
2. **Strategy Pattern**: Pluggable conversion strategies
3. **Registry Pattern**: Central directory of components
4. **Hub-and-Spoke**: Centralized data model
5. **Repository Pattern**: State persistence abstraction

## Performance Considerations

- **Two-hop conversion**: Slight overhead vs direct conversion, but negligible for file I/O
- **State tracking**: Avoids re-syncing unchanged files
- **Lazy loading**: Adapters created only when needed
- **Incremental sync**: Only modified files processed

## Security Considerations

- **Path validation**: Ensure files are in expected directories
- **Content validation**: Verify YAML/JSON structure before parsing
- **Permission checking**: Respect file permissions
- **No code execution**: Pure data conversion, no eval/exec

## Future Enhancements

1. **Batch operations**: Sync multiple directory pairs
2. **Watch mode**: Auto-sync on file changes
3. **Merge strategies**: Beyond newest-wins conflict resolution
4. **Format validation**: Schema validation for each format
5. **Migration scripts**: One-time conversions with custom logic
6. **Web UI**: Visual sync management
7. **API**: Programmatic access to sync engine
