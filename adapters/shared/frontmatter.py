"""
Shared utilities for parsing YAML frontmatter in Markdown files.

Used by adapters that store agents as .md files with YAML frontmatter
(e.g., Claude Code and GitHub Copilot).

This eliminates code duplication and ensures consistent parsing behavior
across different format adapters.
"""

import re
import yaml
from typing import Tuple


def parse_yaml_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Parse YAML frontmatter from Markdown content.

    Expects content in the format:
        ---
        key: value
        another: value
        ---
        Markdown body content...

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Tuple of (frontmatter_dict, body_markdown)
        - frontmatter_dict: Parsed YAML as dictionary
        - body_markdown: Stripped markdown body content

    Raises:
        ValueError: If no valid frontmatter found

    Example:
        >>> content = '''---
        ... name: test-agent
        ... description: Test
        ... ---
        ... Agent instructions'''
        >>> fm, body = parse_yaml_frontmatter(content)
        >>> fm['name']
        'test-agent'
        >>> body
        'Agent instructions'
    """
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found")

    yaml_content, body = match.groups()
    frontmatter = yaml.safe_load(yaml_content)
    return frontmatter, body.strip()


def build_yaml_frontmatter(frontmatter: dict, body: str) -> str:
    """
    Build Markdown content with YAML frontmatter.

    Creates formatted content with frontmatter block and body.

    Args:
        frontmatter: Dictionary of frontmatter fields
        body: Markdown body content

    Returns:
        Complete Markdown content with frontmatter in format:
            ---
            key: value
            ---
            body content

    Example:
        >>> fm = {'name': 'agent', 'description': 'Test'}
        >>> body = 'Instructions here'
        >>> result = build_yaml_frontmatter(fm, body)
        >>> '---' in result
        True
        >>> 'name: agent' in result
        True
    """
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---\n{body}\n"
