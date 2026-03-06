#!/usr/bin/env python3
"""
Scaffold a new Claude Code agent from a template.

Usage:
    python scaffold_agent.py <agent-name> <output-dir> [--type TYPE]

Types:
    subagent     - Standard subagent (.claude/agents/)
    skill        - Skill with SKILL.md (.claude/skills/)
    command      - Slash command (.claude/commands/)
    hook         - Hook script + settings entry
    full-stack   - Complete setup: agent + skill + command + hook

Examples:
    python scaffold_agent.py code-reviewer .claude --type subagent
    python scaffold_agent.py deploy-pipeline .claude --type full-stack
"""

import sys
import os
import json
from pathlib import Path

TEMPLATES = {
    "subagent": {
        "path": "agents/{name}.md",
        "content": """---
name: {name}
description: "{description}"
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a specialized agent for {purpose}.

## When Invoked

1. Understand the task from the prompt
2. Gather necessary context from the codebase
3. Execute the task systematically
4. Report results clearly

## Approach

- Start by reading relevant files to understand context
- Use grep/glob to find related code
- Be thorough but focused on the specific task
- Explain your reasoning as you go

## Output Format

Provide:
- What you found or did
- Key decisions and why
- Any issues or concerns
- Recommended next steps
"""
    },
    "skill": {
        "path": "skills/{name}/SKILL.md",
        "content": """---
name: {name}
description: "{description}"
---

# {title}

## Overview

{purpose}

## Instructions

When this skill is triggered:

1. **Understand the context**: Read the user's request and any relevant files
2. **Apply the procedure**: Follow the steps below
3. **Deliver results**: Present output in the expected format

## Procedure

<!-- Add your detailed instructions here -->

## Examples

**Example 1:**
Input: [describe a typical input]
Output: [describe the expected output]

## Notes

- [Add important caveats or tips]
"""
    },
    "command": {
        "path": "commands/{name}.md",
        "content": """---
description: {description}
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob
---

# {title}: $ARGUMENTS

## Instructions

{purpose}

## Steps

1. **Analyze**: Understand the input from $ARGUMENTS
2. **Research**: Gather context from the codebase
3. **Execute**: Perform the requested action
4. **Report**: Summarize what was done

## Usage

```
/{name} [your input here]
```
"""
    },
    "hook": {
        "script_path": "scripts/hooks/{name}.sh",
        "script_content": """#!/bin/bash
# Hook: {name}
# Description: {description}
#
# This hook runs on {event} events.
# Exit code 0 = allow, exit code 2 = block
#
# Input is received as JSON via stdin.
# Use jq to parse: INPUT=$(cat); echo "$INPUT" | jq '.tool_input'

INPUT=$(cat)

# Parse the tool input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Add your validation logic here
# Example: Block dangerous commands
# if echo "$COMMAND" | grep -qE '(rm -rf|drop table)'; then
#   echo "BLOCKED: Dangerous operation detected"
#   exit 2
# fi

# Allow the operation
exit 0
""",
        "settings_entry": {
            "event": "PreToolUse",
            "matcher": "Bash",
            "command": "./scripts/hooks/{name}.sh"
        }
    }
}


def scaffold_subagent(name, output_dir, description="", purpose=""):
    tmpl = TEMPLATES["subagent"]
    filepath = Path(output_dir) / tmpl["path"].format(name=name)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    content = tmpl["content"].format(
        name=name,
        description=description or f"Specialized agent for {name.replace('-', ' ')}. Use proactively when relevant.",
        purpose=purpose or name.replace("-", " ")
    )
    filepath.write_text(content)
    print(f"  Created: {filepath}")
    return filepath


def scaffold_skill(name, output_dir, description="", purpose=""):
    tmpl = TEMPLATES["skill"]
    filepath = Path(output_dir) / tmpl["path"].format(name=name)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Also create scripts/ dir
    scripts_dir = filepath.parent / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    title = name.replace("-", " ").title()
    content = tmpl["content"].format(
        name=name,
        title=title,
        description=description or f"Provides {title.lower()} capabilities. Trigger when user needs {name.replace('-', ' ')}.",
        purpose=purpose or f"This skill provides {title.lower()} capabilities."
    )
    filepath.write_text(content)
    print(f"  Created: {filepath}")
    print(f"  Created: {scripts_dir}/")
    return filepath


def scaffold_command(name, output_dir, description="", purpose=""):
    tmpl = TEMPLATES["command"]
    filepath = Path(output_dir) / tmpl["path"].format(name=name)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    title = name.replace("-", " ").title()
    content = tmpl["content"].format(
        name=name,
        title=title,
        description=description or f"Run the {title.lower()} workflow",
        purpose=purpose or f"Executes the {title.lower()} workflow on the given input."
    )
    filepath.write_text(content)
    print(f"  Created: {filepath}")
    return filepath


def scaffold_hook(name, output_dir, description="", event="PreToolUse"):
    tmpl = TEMPLATES["hook"]
    script_path = Path(output_dir).parent / tmpl["script_path"].format(name=name)
    script_path.parent.mkdir(parents=True, exist_ok=True)

    script_content = tmpl["script_content"].format(
        name=name,
        description=description or f"Validates operations for {name.replace('-', ' ')}",
        event=event
    )
    script_path.write_text(script_content)
    os.chmod(script_path, 0o755)
    print(f"  Created: {script_path}")

    # Show the settings.json entry
    entry = tmpl["settings_entry"]
    settings_snippet = {
        "hooks": {
            entry["event"]: [{
                "matcher": entry["matcher"],
                "hooks": [{
                    "type": "command",
                    "command": entry["command"].format(name=name)
                }]
            }]
        }
    }
    print(f"  Add to .claude/settings.json:")
    print(f"  {json.dumps(settings_snippet, indent=2)}")
    return script_path


def scaffold_full_stack(name, output_dir, description="", purpose=""):
    print(f"\nScaffolding full-stack agent: {name}")
    print(f"{'=' * 50}")

    print("\n[Subagent]")
    scaffold_subagent(name, output_dir, description, purpose)

    print("\n[Skill]")
    scaffold_skill(name, output_dir, description, purpose)

    print("\n[Slash Command]")
    scaffold_command(name, output_dir, description, purpose)

    print("\n[Hook]")
    scaffold_hook(name, output_dir, description)

    print(f"\n{'=' * 50}")
    print(f"Full-stack agent '{name}' scaffolded!")
    print(f"\nNext steps:")
    print(f"  1. Edit the agent file to add specific instructions")
    print(f"  2. Customize the skill with domain knowledge")
    print(f"  3. Adjust the slash command workflow")
    print(f"  4. Update the hook script with validation logic")
    print(f"  5. Add the hook entry to .claude/settings.json")
    print(f"  6. Test with: claude then type /{name} <your input>")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    name = sys.argv[1]
    output_dir = sys.argv[2]
    agent_type = "subagent"

    for i, arg in enumerate(sys.argv):
        if arg == "--type" and i + 1 < len(sys.argv):
            agent_type = sys.argv[i + 1]

    scaffolders = {
        "subagent": scaffold_subagent,
        "skill": scaffold_skill,
        "command": scaffold_command,
        "hook": scaffold_hook,
        "full-stack": scaffold_full_stack,
    }

    if agent_type not in scaffolders:
        print(f"Unknown type: {agent_type}. Valid: {', '.join(scaffolders.keys())}")
        sys.exit(1)

    scaffolders[agent_type](name, output_dir)


if __name__ == "__main__":
    main()
