#!/usr/bin/env python3
"""
Validate Claude Code agent files for common issues.

Usage:
    python validate_agents.py <path-to-agents-dir>
    python validate_agents.py .claude/agents/
    python validate_agents.py ~/.claude/agents/

Checks:
- YAML frontmatter is valid
- Required fields (name, description) are present
- Tool names are valid Claude Code tools
- Description quality (specificity, length, trigger keywords)
- System prompt quality (length, structure)
- File naming conventions
"""

import sys
import os
import re
import yaml
from pathlib import Path

VALID_TOOLS = {
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task", "Skill",
    "AskUserQuestion", "TodoRead", "TodoWrite",
}

VALID_MODELS = {"sonnet", "opus", "haiku", "inherit"}

VALID_PERMISSION_MODES = {
    "default", "acceptEdits", "bypassPermissions", "plan", "ignore"
}

TRIGGER_KEYWORDS = [
    "proactively", "use when", "invoke when", "must be used",
    "use immediately", "use after", "trigger when"
]


class ValidationResult:
    def __init__(self, filepath):
        self.filepath = filepath
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    @property
    def passed(self):
        return len(self.errors) == 0

    def __str__(self):
        lines = [f"\n{'=' * 60}", f"  {self.filepath}", f"{'=' * 60}"]
        if self.errors:
            lines.append(f"\n  ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"    ✗ {e}")
        if self.warnings:
            lines.append(f"\n  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"    ⚠ {w}")
        if self.info:
            lines.append(f"\n  INFO:")
            for i in self.info:
                lines.append(f"    ℹ {i}")
        if self.passed and not self.warnings:
            lines.append("\n  ✓ All checks passed!")
        return "\n".join(lines)


def parse_frontmatter(content):
    """Extract YAML frontmatter and body from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)', content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm, match.group(2).strip()
    except yaml.YAMLError as e:
        return {"_parse_error": str(e)}, match.group(2).strip()


def validate_agent_file(filepath):
    """Validate a single agent file."""
    result = ValidationResult(filepath)

    # Read file
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        result.error(f"Cannot read file: {e}")
        return result

    if not content.strip():
        result.error("File is empty")
        return result

    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)

    if frontmatter is None:
        result.error("No YAML frontmatter found (must start with ---)")
        return result

    if "_parse_error" in frontmatter:
        result.error(f"Invalid YAML in frontmatter: {frontmatter['_parse_error']}")
        return result

    # Required fields
    if not frontmatter.get("name"):
        result.error("Missing required field: name")
    else:
        name = frontmatter["name"]
        if not re.match(r'^[a-z][a-z0-9-]*$', name):
            result.warn(f"Name '{name}' should use lowercase letters and hyphens only")

    if not frontmatter.get("description"):
        result.error("Missing required field: description")
    else:
        desc = frontmatter["description"]
        # Check description quality
        if len(desc) < 20:
            result.warn(f"Description is very short ({len(desc)} chars). Longer descriptions trigger better.")
        elif len(desc) < 50:
            result.warn(f"Description could be more specific ({len(desc)} chars). Aim for 50-200 chars.")

        has_trigger = any(kw in desc.lower() for kw in TRIGGER_KEYWORDS)
        if not has_trigger:
            result.warn(
                "Description lacks trigger keywords like 'Use proactively', "
                "'Invoke when', 'Use immediately after'. Adding these improves auto-delegation."
            )

    # Tools validation
    if "tools" in frontmatter and frontmatter["tools"]:
        tools_str = frontmatter["tools"]
        if isinstance(tools_str, str):
            tools = [t.strip() for t in tools_str.split(",")]
        elif isinstance(tools_str, list):
            tools = tools_str
        else:
            tools = []
            result.warn(f"Unexpected tools format: {type(tools_str)}")

        for tool in tools:
            # Allow MCP tool patterns like mcp__server__tool
            if tool.startswith("mcp__"):
                continue
            if tool not in VALID_TOOLS:
                result.warn(f"Unknown tool: '{tool}'. Valid tools: {', '.join(sorted(VALID_TOOLS))}")

        if "Task" in tools and len(tools) == 1:
            result.warn("Agent has only Task tool. It can delegate but not do anything itself.")

    # Model validation
    if "model" in frontmatter and frontmatter["model"]:
        model = str(frontmatter["model"])
        if model not in VALID_MODELS:
            result.warn(f"Unknown model alias: '{model}'. Valid: {', '.join(VALID_MODELS)}")

    # Permission mode validation
    if "permissionMode" in frontmatter and frontmatter["permissionMode"]:
        mode = frontmatter["permissionMode"]
        if mode not in VALID_PERMISSION_MODES:
            result.warn(f"Unknown permissionMode: '{mode}'. Valid: {', '.join(VALID_PERMISSION_MODES)}")

        if mode == "bypassPermissions":
            result.warn("bypassPermissions mode skips all safety checks. Use with caution.")

    # Body (system prompt) validation
    if not body:
        result.error("No system prompt (markdown body) found. The agent needs instructions.")
    else:
        word_count = len(body.split())
        if word_count < 20:
            result.warn(f"System prompt is very short ({word_count} words). More detail usually helps.")
        elif word_count > 2000:
            result.warn(f"System prompt is very long ({word_count} words). Consider moving details to a skill.")

        # Check for good patterns
        if re.search(r'(?:^|\n)#+\s', body):
            result.note("Uses headers for structure (good)")
        if re.search(r'\d+\.', body):
            result.note("Uses numbered steps (good)")
        if "when invoked" in body.lower() or "when called" in body.lower():
            result.note("Includes invocation instructions (good)")

    # Filename check
    filename = os.path.basename(filepath)
    if not filename.endswith(".md"):
        result.error("Agent file must have .md extension")
    name_part = filename.replace(".md", "")
    if frontmatter.get("name") and frontmatter["name"] != name_part:
        result.note(
            f"Filename '{name_part}' differs from frontmatter name '{frontmatter['name']}'. "
            "Frontmatter name takes precedence."
        )

    return result


def validate_directory(dir_path):
    """Validate all agent files in a directory."""
    dir_path = Path(dir_path)
    if not dir_path.exists():
        print(f"Error: Directory not found: {dir_path}")
        sys.exit(1)

    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {dir_path}")
        sys.exit(0)

    results = []
    for f in md_files:
        results.append(validate_agent_file(str(f)))

    # Print results
    total_errors = 0
    total_warnings = 0
    for r in results:
        print(r)
        total_errors += len(r.errors)
        total_warnings += len(r.warnings)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  SUMMARY: {len(results)} files checked")
    print(f"  {total_errors} errors, {total_warnings} warnings")
    print(f"{'=' * 60}")

    return total_errors == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_agents.py <path-to-agents-dir-or-file>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        result = validate_agent_file(target)
        print(result)
        sys.exit(0 if result.passed else 1)
    else:
        success = validate_directory(target)
        sys.exit(0 if success else 1)
