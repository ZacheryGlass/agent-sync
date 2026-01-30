# Agent Sync

A universal synchronization tool for custom agents, permissions, and slash commands (saved prompts) between **Claude Code** and **GitHub Copilot**.

**Support for Codex and Gemini CLI coming soon!**

Manage your configuration in your preferred tool's native settings files, and automatically sync and convert those changes to all your other supported AI coding agents.

## Features

- **Bidirectional Sync:** Automatically syncs changes in both directions between Claude and Copilot configurations.
- **Permission Management:** Translates and syncs permission configurations (Claude `settings.json` ↔ Copilot `.perm.json`).
- **Slash Commands:** Syncs slash command definitions and prompt files.
- **Smart Conflict Resolution:** Detects conflicts and offers interactive or automatic resolution strategies.
- **State Tracking:** Intelligently tracks file modifications and deletions to keep directories clean.
- **Format Conversion:** Seamlessly converts between format-specific schemas (e.g., Markdown structure, YAML frontmatter).
- **Dry-Run Mode:** Preview changes safely before applying them to your file system.

## Installation

The recommended way to install Agent Sync is via pip:

```bash
pip install agent-sync
```

### Building from Source

If you prefer to build from source:

**Requirements:** Python 3.8+

```bash
# Clone the repository
git clone https://github.com/ZacheryGlass/agent-sync.git
cd agent-sync

# Install dependencies
pip install -r requirements.txt

# Run via module
python -m cli.main
```

## Usage

Agent Sync is a Command Line Interface (CLI) tool with subcommands for different operations.

### Quick Start

```bash
# Sync configurations between Claude and Copilot
agent-sync sync --source-format claude --target-format copilot

# View available commands
agent-sync --help

# Get help for a specific command
agent-sync sync --help
```

### Available Commands

- **`agent-sync sync`**: Run a one-off synchronization between formats (main command)
- **`agent-sync init`**: Initialize agent-sync configuration (coming soon)
- **`agent-sync watch`**: Watch and sync changes in real-time (coming soon)
- **`agent-sync config`**: View or edit configuration (coming soon)

### Sync Command

The `sync` command is the primary tool for synchronizing configurations.

#### Basic Syntax

```bash
agent-sync sync [options]
```

#### Common Examples

```bash
# Auto-discover profile paths and sync
agent-sync sync --source-format claude --target-format copilot

# Sync specific directories
agent-sync sync --source-dir ~/.claude --target-dir .github \
                --source-format claude --target-format copilot

# Sync only agents (skip permissions and commands)
agent-sync sync --source-dir ~/.claude --target-dir .github \
                --source-format claude --target-format copilot --only agents

# Single file conversion
agent-sync sync --convert-file ~/.claude/agents/planner.md --target-format copilot

# Dry-run (preview changes without applying)
agent-sync sync --source-dir ~/.claude --target-dir .github \
                --source-format claude --target-format copilot --dry-run
```

### Sync Options

The tool offers various flags to customize the synchronization process.

#### Core Configuration
- **`--source-dir`**: Specifies the directory containing your source configuration files.
- **`--target-dir`**: Specifies the directory where files should be synced to.
- **`--source-format`**: Defines the format of the source files (`claude`, `copilot`, or `gemini`).
- **`--target-format`**: Defines the format for the destination files (`claude`, `copilot`, or `gemini`).
- **`--only`**: Filter to specific config types (comma-separated: `agents`, `commands`, `permissions`). By default, syncs all detected types.
- **`--direction`**: Controls the synchronization flow.
    - `both`: Bidirectional sync (default).
    - `source-to-target`: One-way sync from source to target.
    - `target-to-source`: One-way sync from target to source.

#### Operation Control
- **`--dry-run`**: Simulates the operation and prints what would happen without modifying any files.
- **`--force`**: Automatically resolves conflicts by choosing the newest file, bypassing interactive prompts.
- **`--yes`, `-y`**: Skip confirmation prompts (useful for scripts/CI).
- **`--state-file`**: Path to a custom state file (defaults to `~/.agent_sync_state.json`). This file tracks sync history.
- **`--verbose`, `-v`**: Enables detailed logging output for debugging.
- **`--strict`**: Error on lossy conversions (e.g., Claude deny rules downgraded to VS Code ask).

#### Single File Operations
- **`--convert-file`**: Path to a single file to convert. Mutually exclusive with directory options.
- **`--output`**: Destination path for the single converted file (auto-generated if not specified).
- **`--sync-file`** & **`--target-file`**: Used for in-place merging of two specific files.
- **`--bidirectional`**: Sync changes in both directions for in-place merge mode.

#### Format-Specific Flags
- **`--add-argument-hint`**: Adds an `argument-hint` field (useful for Copilot) when converting from Claude.
- **`--add-handoffs`**: Adds a `handoffs` placeholder field when converting to Copilot format.
- **`--no-autodiscover`**: Disable auto-discovery; require explicit --source-dir and --target-dir.

### Legacy Mode (Deprecated)

The flat-argument style without subcommands is still supported for backward compatibility but will be removed in version 3.0:

```bash
# Old style (deprecated)
agent-sync --source-format claude --target-format copilot

# New style (recommended)
agent-sync sync --source-format claude --target-format copilot
```

When using the old style, a deprecation warning is displayed.

## Configuration Details

### File Matching Strategy
Files are matched between formats based on their base names:
- **Agents:** `planner.md` (Claude) ↔ `planner.agent.md` (Copilot)
- **Permissions:** `settings.json` (Claude) ↔ `settings.perm.json` (Copilot)
- **Slash Commands:** `command.md` (Claude) ↔ `command.prompt.md` (Copilot)

### Field Mapping

#### Claude → Copilot
| Claude Field | Copilot Field | Notes |
|--------------|---------------|-------|
| `name` | `name` | Direct mapping |
| `description` | `description` | Direct mapping |
| `description` | `argument-hint` | Optional (requires `--add-argument-hint`) |
| `tools` | `tools` | Converts comma-separated string to array |
| `model` | `model` | Maps model names (e.g., `sonnet` → `Claude Sonnet 4`) |
| `permissionMode` | - | Dropped (handled via Permission Sync) |

#### Copilot → Claude
| Copilot Field | Claude Field | Notes |
|---------------|--------------|-------|
| `name` | `name` | Direct mapping |
| `description` | `description` | Direct mapping |
| `tools` | `tools` | Converts array to comma-separated string |
| `model` | `model` | Maps model names (e.g., `Claude Sonnet 4` → `sonnet`) |
| `argument-hint` | - | Dropped |

### Permission Conversion

The tool handles complex logic to translate between Claude's permission system and VS Code's (Copilot) permission structure.

**VS Code (Copilot)** uses specific boolean flags for commands and URLs (e.g., `"chat.tools.terminal.autoApprove"`).
**Claude Code** uses categories (`allow`, `ask`, `deny`) with specific patterns.

- **Auto-Approve:** Maps between VS Code `true` and Claude `allow`.
- **Require Approval:** Maps between VS Code `false` and Claude `ask`.
- **Regex Patterns:** Preserved as-is during conversion.
- **Lossy Conversions:** Since VS Code does not support a hard "deny" (block) state, Claude `deny` rules are converted to "require approval" in VS Code, and a warning is logged.

## Contributing

Contributions are welcome! Please submit a Pull Request or open an issue to discuss proposed changes.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
