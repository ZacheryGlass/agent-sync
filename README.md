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

**Automated Releases:**
Simply push a tag starting with `v` (e.g., `v1.0.0`) to the repository. The workflow will automatically:
1. Build the binaries for Linux and Windows.
2. Create a new GitHub Release.
3. Upload the binaries as assets.
4. Generate release notes from the commit history.

**Manual Trigger:**
1. Go to the "Actions" tab in the repository.
2. Select "Build and Release".
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

Sync permission configurations between VS Code (Copilot) and Claude Code formats:

**VS Code (Copilot) → Claude:**
```bash
python -m cli.main \
  --source-dir ~/.vscode \
  --target-dir ~/.claude \
  --source-format copilot \
  --target-format claude \
  --config-type permission
```

**Claude → VS Code (Copilot):**
```bash
python -m cli.main \
  --source-dir ~/.claude \
  --target-dir .github \
  --source-format claude \
  --target-format copilot \
  --config-type permission
```

**Bidirectional sync:**
```bash
python -m cli.main \
  --source-dir ~/.claude \
  --target-dir ~/.vscode \
  --source-format claude \
  --target-format copilot \
  --config-type permission
```

See [Permission Conversion Details](#permission-conversion) below for more information.

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

## Permission Conversion

The tool supports bidirectional conversion of permission configurations between VS Code (Copilot) and Claude Code formats.

### Permission Format Overview

**VS Code (Copilot) Format:**
```json
{
  "chat.tools.terminal.autoApprove": {
    "mkdir": true,
    "/^git status$/": true,
    "rm": false,
    "/dangerous/": false
  },
  "chat.tools.urls.autoApprove": {
    "https://*.github.com/*": true,
    "https://untrusted.com": false
  }
}
```

**Claude Code Format:**
```json
{
  "permissions": {
    "allow": [
      "Bash(mkdir:*)",
      "Bash(/^git status$/)",
      "WebFetch(domain:*.github.com)"
    ],
    "ask": [
      "Bash(rm:*)",
      "Bash(/dangerous/)",
      "WebFetch(domain:untrusted.com)"
    ],
    "deny": []
  }
}
```

### Conversion Rules

#### VS Code → Claude

| VS Code Setting | Claude Category | Description |
|-----------------|-----------------|-------------|
| `"command": true` | `allow` | Auto-approve (no prompt) |
| `"command": false` | `ask` | Require approval before execution |
| `/regex/: true` | `allow` | Regex patterns preserved |
| `/regex/: false` | `ask` | Regex patterns preserved |
| Terminal commands | `Bash()` permissions | Simple strings become `Bash(cmd:*)`, regex stays as-is |
| URL patterns | `WebFetch(domain:...)` | Domain extracted from URL |

#### Claude → VS Code

| Claude Category | VS Code Setting | Notes |
|-----------------|-----------------|-------|
| `allow` | `true` | Auto-approve |
| `ask` | `false` | Require approval |
| `deny` | `false` (with warning) | **Lossy conversion** - VS Code doesn't support blocking entirely |
| `Bash()` rules | Terminal commands | Pattern extracted from `Bash(pattern)` |
| `WebFetch()` rules | URL patterns | Domain becomes `https://domain/*` |

### Important Notes

#### 1. Lossy Conversions

When converting Claude `deny` rules to VS Code format, they become `false` (require approval) instead of blocking entirely. This is because VS Code doesn't have a true "deny" concept.

**Example:**
```json
// Claude
{
  "permissions": {
    "deny": ["Bash(rm -rf:*)"]
  }
}

// Converts to VS Code as:
{
  "chat.tools.terminal.autoApprove": {
    "rm -rf": false  // Require approval, not blocked
  }
}
```

The tool generates warnings for these lossy conversions.

#### 2. Regex Pattern Handling

Regex patterns are preserved as-is during conversion:

```json
// VS Code
{
  "chat.tools.terminal.autoApprove": {
    "/^git (status|show\\b.*)$/": true
  }
}

// Converts to Claude as:
{
  "permissions": {
    "allow": ["Bash(/^git (status|show\\b.*)$/)"]
  }
}
```

#### 3. URL Split Approval

VS Code supports separate approval for request vs response (`approveRequest` / `approveResponse`). Claude doesn't support this granularity, so split approvals map to `ask` (safer) with original details stored in metadata.

**Example:**
```json
// VS Code
{
  "chat.tools.urls.autoApprove": {
    "https://api.example.com/*": {
      "approveRequest": true,
      "approveResponse": false
    }
  }
}

// Converts to Claude as:
{
  "permissions": {
    "ask": ["WebFetch(domain:api.example.com)"]
  }
  // Metadata stores original split approval details
}
```

#### 4. Round-Trip Fidelity

For VS Code → Claude → VS Code conversions (without `deny` rules), perfect fidelity is maintained:

```bash
# Convert VS Code → Claude
python -m cli.main --convert-file vscode-settings.json --target-format claude

# Convert back Claude → VS Code
python -m cli.main --convert-file claude-settings.json --target-format copilot

# Result: Identical to original vscode-settings.json
```

### Examples

See `examples/permission_conversion_example.py` for complete working examples of:
- VS Code → Claude conversion
- Claude → VS Code conversion
- Lossy conversion tracking
- Round-trip conversion
- Complex URL permissions

Run the examples:
```bash
PYTHONPATH=/workspaces/coding-agent-settings-sync python examples/permission_conversion_example.py
```

### Conversion Warnings

The tool tracks and reports conversion warnings. Examples of warnings:
- Lossy conversions (Claude `deny` → VS Code `false`)
- Unsupported features (split URL approvals)
- Pattern transformations

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