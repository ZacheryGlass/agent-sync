# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles
- Never use emojis.
- Never add Claude as a commit author.
- Always commit using the default git settings.
- Never create .md files unless explicitly instructed.

## Project Overview

This is a universal synchronization tool for AI coding agent configurations. It supports syncing between multiple AI tools (Claude Code, GitHub Copilot, and others) and multiple config types (agents, permissions, prompts).

The project uses a hub-and-spoke architecture with canonical data models, enabling N-way sync with 2N converters instead of N² converters.

## Commands

### Legacy Script (Currently Functional)
```bash
# Install dependencies
pip install -r requirements.txt

# The original script still works for Claude <-> Copilot sync
python sync_custom_agents.py \
  --claude-dir ~/.claude/agents \
  --copilot-dir ./.github/agents \
  --dry-run

# Force automatic conflict resolution
python sync_custom_agents.py \
  --claude-dir ~/.claude/agents \
  --copilot-dir ./.github/agents \
  --force --verbose
```

### New CLI (Under Development)
```bash
# Universal sync between any formats
python -m cli.main \
  --source-dir ~/.claude/agents \
  --target-dir .github/agents \
  --source-format claude \
  --target-format copilot \
  --config-type agent \
  --dry-run

# Single-file conversion
python -m cli.main \
  --convert-file ~/.claude/agents/planner.md \
  --target-format copilot \
  --output .github/agents/planner.agent.md

# Auto-detect formats and auto-generate output filename
python -m cli.main \
  --convert-file my-agent.md \
  --target-format copilot
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_adapters.py -v

# Run tests matching pattern
pytest tests/ -k "test_claude"
```

#### Testing Philosophy: Integration-Style Tests
This project uses integration-style testing rather than heavily mocked unit tests:

- **Real objects over mocks**: Tests use actual adapter implementations (ClaudeAdapter, CopilotAdapter) rather than mocking them
- **Real file I/O**: Tests use pytest's `tmp_path` fixture for actual file operations
- **Minimal mocking**: Only mock external dependencies like user input (`input()`) when necessary
- **Full pipeline verification**: Tests verify the complete conversion flow (file -> adapter -> canonical -> adapter -> file)

This approach catches real integration issues like format parsing errors, file extension handling, and encoding problems that mocked tests would miss.

## Architecture

### New Architecture (Hub-and-Spoke with Canonical Models)

The new architecture supports N formats with 2N converters instead of N²:

```
Format A → Canonical Model ← Format B
                ↓
            Format C
```

**Core Modules:**

1. **core/canonical_models.py**
   - `CanonicalAgent`: Universal agent representation
   - `CanonicalPermission`: Universal permission representation
   - `CanonicalPrompt`: Universal prompt representation
   - Metadata dictionary preserves format-specific fields for round-trip fidelity

2. **core/adapter_interface.py**
   - `FormatAdapter`: Abstract base class for all format converters
   - Defines contract: `to_canonical()` and `from_canonical()`
   - Each format implements this interface once

3. **core/registry.py**
   - `FormatRegistry`: Central directory of available adapters
   - Auto-detects format from file paths
   - Validates format support for config types

4. **core/orchestrator.py**
   - `UniversalSyncOrchestrator`: Coordinates sync operations
   - Works with any source/target format pair
   - Handles conflicts, state tracking, dry-run mode

5. **core/state_manager.py**
   - `SyncStateManager`: Tracks sync history in `~/.agent_sync_state.json`
   - Enables intelligent change detection
   - Prevents unnecessary syncs

**Format Adapters:**

6. **adapters/claude.py** - Claude Code (.md files)
7. **adapters/copilot.py** - GitHub Copilot (.agent.md files)
8. **adapters/example.py** - Template for new adapter implementations

### Legacy Architecture (sync_custom_agents.py)

The original implementation remains functional for Claude <-> Copilot sync:

1. **AgentConverter** (sync_custom_agents.py:93-246)
   - Bidirectional Claude/Copilot conversion
   - Hardcoded field mappings

2. **SyncState** (sync_custom_agents.py:31-91)
   - State tracking (same format as new architecture)

3. **AgentSyncer** (sync_custom_agents.py:249-595)
   - Orchestration specific to Claude/Copilot

### Key Design Decisions

- **Canonical Model**: All formats convert to/from universal representation
- **Information Preservation**: Metadata dict stores format-specific fields
- **Scalability**: Adding format N+1 requires only 2 converters, not 2N
- **File matching**: Agents matched by base name (e.g., `planner.md` ↔ `planner.agent.md`)
- **Conflict resolution**: Without `--force`, prompts user; with `--force`, uses newest file
- **State tracking**: Stored in `~/.agent_sync_state.json` to work across projects
- **Layered Validation**: CLI validates paths exist and are accessible (fail fast at user boundary); Orchestrator validates format/config type compatibility (business logic)

### Conversion Flow

```
Source Format → Adapter.read() → to_canonical() → CanonicalAgent
    ↓
CanonicalAgent → from_canonical() → Adapter.write() → Target Format
```

Each adapter handles:
- Parsing format-specific structure
- Normalizing field names and types
- Model name mapping
- Tool format conversion
- Preserving unique fields in metadata

## Dependencies

- Python 3.x
- PyYAML: For parsing YAML frontmatter in agent files
- requests: For HTTP fetching in documentation sync
- beautifulsoup4: For HTML parsing
- html2text: For HTML to markdown conversion

## File Locations

### Project Structure
```
agent-sync/
├── core/                      # Core architecture modules
│   ├── canonical_models.py    # Universal data models
│   ├── adapter_interface.py   # Adapter contract
│   ├── registry.py            # Format registry
│   ├── orchestrator.py        # Sync orchestrator
│   └── state_manager.py       # State tracking
├── adapters/                  # Format adapters
│   ├── claude.py             # Claude Code adapter
│   ├── copilot.py            # GitHub Copilot adapter
│   └── example.py            # Template for new adapters
├── cli/                       # Command-line interface
│   └── main.py               # CLI entry point
├── scripts/                   # Utility scripts
│   └── sync_docs.py          # Documentation sync script
├── docs/                      # Documentation
│   └── permissions/          # Permission research docs
├── tests/                     # Test suite
│   ├── test_adapters.py      # Adapter tests
│   ├── test_registry.py      # Registry tests
│   ├── test_orchestrator.py  # Orchestrator tests
│   ├── test_state_manager.py # State manager tests
│   ├── test_cli.py           # CLI tests
│   ├── test_sync_docs.py     # Documentation sync tests
│   └── fixtures/             # Sample files
├── sync_custom_agents.py      # Legacy script (FUNCTIONAL)
├── requirements.txt
└── CLAUDE.md
```

### Configuration Locations
- User sync state: `~/.agent_sync_state.json` (auto-created)
- Claude agents: `~/.claude/agents/` or `.claude/agents/`
- Copilot agents: `.github/agents/`

## Development Status

**Functional:**
- Legacy sync_custom_agents.py (Claude ↔ Copilot)
- Core canonical models
- Claude and Copilot adapters
- Format registry
- State manager
- CLI interface (directory sync and single-file conversion)
- Universal orchestrator

**In Development:**
- Test suite (partial coverage)

## Adding New Format Support

1. Create adapter in `adapters/newformat.py`:
   ```python
   class NewFormatAdapter(FormatAdapter):
       def to_canonical(self, content, config_type): ...
       def from_canonical(self, canonical_obj, config_type): ...
   ```

2. Register in application:
   ```python
   registry.register(NewFormatAdapter())
   ```

3. Add tests in `tests/test_adapters.py`
4. Add fixtures in `tests/fixtures/newformat/`
- Keep all documentation very concise. Only what the engineers need to know.
- All documentation is for the application developers. Not for the users!
