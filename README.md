# Agent Sync Tool

Bidirectional synchronization tool for custom agents and settings between Claude Code and GitHub Copilot.

## Features

- ✅ **Bidirectional sync** - Sync in both directions automatically
- ✅ **Permission sync** - Sync permission configurations (Claude `settings.json` ↔ Copilot `.perm.json`)
- ✅ **Smart conflict resolution** - Handles conflicts with user prompts or auto-resolution
- ✅ **Deletion tracking** - Removes agents deleted from source
- ✅ **Modification tracking** - Only syncs changed files using state tracking
- ✅ **Format conversion** - Automatic conversion between `.md` and `.agent.md` formats
- ✅ **Field mapping** - Intelligent mapping of format-specific fields
- ✅ **Dry-run mode** - Preview changes before applying

## Building Standalone Executable

You can package the application as a standalone executable (no Python installation required) for Linux or Windows.

### Using GitHub Actions (Recommended)

This repository includes a GitHub Action to automatically build both Linux and Windows binaries.
1. Go to the "Actions" tab in the repository.
2. Select "Build Standalone Executable".
3. Click "Run workflow".
4. Download the artifacts from the completed run.

### Building Manually

**Linux:**
Run the provided build script:
```bash
./scripts/build_executable.sh
```
The executable will be located at `dist/agent-sync`.

**Windows:**
Run the following command in a terminal (PowerShell or Command Prompt) with Python installed:
```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean agent-sync.spec
```
The executable will be located at `dist/agent-sync.exe`.

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

The tool is run via the `cli.main` module.

### GUI Mode

Launch the graphical user interface by running the tool without arguments or with the `--gui` flag:

```bash
# Launch GUI (default if no args)
python -m cli.main

# Or explicitly
python -m cli.main --gui
```

### Basic Bidirectional Agent Sync

```bash
python -m cli.main \
  --source-dir ~/.claude/agents \
  --target-dir .github/agents \
  --source-format claude \
  --target-format copilot \
  --config-type agent
```

### Permission Sync

Sync Claude permissions (`settings.json`) to Copilot (placeholder files):

```bash
python -m cli.main \
  --source-dir ~/.claude \
  --target-dir .github \
  --source-format claude \
  --target-format copilot \
  --config-type permission
```

### One-Time Migration

**Claude → Copilot:**
```bash
python -m cli.main \
  --source-dir ~/.claude/agents \
  --target-dir .github/agents \
  --source-format claude \
  --target-format copilot \
  --config-type agent \
  --direction source-to-target
```

**Copilot → Claude:**
```bash
python -m cli.main \
  --source-dir .github/agents \
  --target-dir ~/.claude/agents \
  --source-format copilot \
  --target-format claude \
  --config-type agent \
  --direction source-to-target
```

### Preview Changes (Dry Run)

```bash
python -m cli.main \
  --source-dir ~/.claude/agents \
  --target-dir .github/agents \
  --source-format claude \
  --target-format copilot \
  --config-type agent \
  --dry-run
```

### With Enhanced Copilot Features

```bash
python -m cli.main \
  --source-dir ~/.claude/agents \
  --target-dir .github/agents \
  --source-format claude \
  --target-format copilot \
  --config-type agent \
  --direction source-to-target \
  --add-argument-hint \
  --add-handoffs
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--source-dir` | Yes | - | Path to source directory containing configuration files |
| `--target-dir` | Yes | - | Path to target directory |
| `--source-format` | Yes | - | Source format name (`claude` or `copilot`) |
| `--target-format` | Yes | - | Target format name (`claude` or `copilot`) |
| `--config-type` | No | `agent` | Type of configuration to sync: `agent` or `permission` |
| `--direction` | No | `both` | Sync direction: `source-to-target`, `target-to-source`, or `both` |
| `--dry-run` | No | `false` | Show changes without applying them |
| `--force` | No | `false` | Auto-resolve conflicts using newest file |
| `--verbose`, `-v` | No | `false` | Detailed logging output |
| `--state-file` | No | `~/.agent_sync_state.json` | Custom path for state file |
| `--add-argument-hint` | No | `false` | Add `argument-hint` field (Claude→Copilot only) |
| `--add-handoffs` | No | `false` | Add `handoffs` placeholder (Claude→Copilot only) |
| `--gui` | No | `false` | Launch the graphical user interface |

## How It Works

### File Matching

Files are matched by base name:
- Agents: `planner.md` (Claude) ↔ `planner.agent.md` (Copilot)
- Permissions: `settings.json` (Claude) ↔ `settings.perm.json` (Copilot)

### Sync Logic

1. **First Sync**: Uses the newest file based on modification time
2. **Subsequent Syncs**: Only syncs files modified since last sync
3. **Conflicts**: When both files are modified:
   - Without `--force`: Prompts user to choose
   - With `--force`: Uses newest file automatically
4. **Deletions**: Removes target file when source is deleted

## Field Conversions

### Claude → Copilot

| Claude Field | Copilot Field | Conversion |
|--------------|---------------|------------|
| `name` | `name` | Direct |
| `description` | `description` | Direct |
| `description` | `argument-hint` | Optional (with `--add-argument-hint`) |
| `tools` | `tools` | String → Array (`"tool1, tool2"` → `['tool1', 'tool2']`) |
| `model` | `model` | Mapped (`sonnet` → `Claude Sonnet 4`) |
| - | `target` | Added (`vscode`) |
| - | `handoffs` | Optional placeholder (with `--add-handoffs`) |
| `permissionMode` | - | **Dropped** (See Permission Sync) |
| `skills` | - | **Dropped** |

### Copilot → Claude

| Copilot Field | Claude Field | Conversion |
|---------------|--------------|------------|
| `name` | `name` | Direct |
| `description` | `description` | Direct |
| `tools` | `tools` | Array → String (`['tool1', 'tool2']` → `"tool1, tool2"`) |
| `model` | `model` | Mapped (`Claude Sonnet 4` → `sonnet`) |
| `argument-hint` | - | **Dropped** |
| `handoffs` | - | **Dropped** |
| `target` | - | **Dropped** |
| `mcp-servers` | - | **Dropped** |

## Troubleshooting

### "No YAML frontmatter found"

Ensure your agent files have proper YAML frontmatter:
```markdown
---
name: agent-name
description: Agent description
---

Body content here
```

### Conflicts Keep Appearing

Use `--force` to automatically resolve conflicts, or manually review and edit the files to resolve differences.

### State File Issues

If sync state gets corrupted, you can safely delete it (default: `~/.agent_sync_state.json`). The next sync will treat all files as new.