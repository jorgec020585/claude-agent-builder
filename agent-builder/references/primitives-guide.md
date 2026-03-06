# Claude Code Primitives Guide

A complete reference for every building block available when designing agents in Claude Code. Use this to make architecture decisions.

---

## 1. Subagents

**What they are**: Specialized AI assistants with their own context window, system prompt, tool permissions, and optional model selection. Defined as Markdown files with YAML frontmatter.

**Where they live**:
- Project-level: `.claude/agents/<name>.md` (highest priority)
- User-level: `~/.claude/agents/<name>.md` (available across all projects)
- CLI-defined: `--agents '{...}'` flag (session-only, good for testing)
- Plugin-provided: Inside plugin `agents/` directories

**When to use**:
- Task needs isolated context (won't pollute main conversation)
- Task is complex enough to benefit from specialized instructions
- You want different tool access than the main agent
- You need parallel execution (multiple subagents can run simultaneously)
- You want a different model (e.g., haiku for speed, opus for depth)

**When NOT to use**:
- Simple one-off tasks that don't need isolation
- Tasks where context from the main conversation is essential
- When a skill or CLAUDE.md instruction would suffice

**Key frontmatter fields**:
```yaml
---
name: agent-name              # Required. Lowercase + hyphens
description: When to use      # Required. The trigger mechanism
tools: Read, Grep, Bash       # Optional. Omit to inherit all tools
model: sonnet                 # Optional. sonnet|opus|haiku|inherit
permissionMode: default       # Optional. default|acceptEdits|bypassPermissions|plan
skills: skill1, skill2        # Optional. Auto-load these skills
memory: user                  # Optional. Persistent memory scope (user|project)
hooks:                        # Optional. Event hooks for this agent
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
maxTurns: 20                  # Optional. Limit conversation turns
mcpServers:                   # Optional. MCP servers for this agent
  - name: my-server
---
```

**Built-in subagents** (always available):
- **General-purpose**: Sonnet model, all tools, read+write. For complex multi-step tasks.
- **Explore**: Haiku model, read-only tools. For fast codebase search and analysis.
- **Plan**: Sonnet model, read-only. Used automatically in plan mode.

**Important constraints**:
- Subagents CANNOT spawn other subagents (no nesting)
- Invoked via the Task tool only — never via shell commands
- Each subagent starts with a clean context (no memory of previous invocations unless using `memory` or `resume`)
- Subagents can be resumed by their `agentId` to continue a previous conversation

**Description writing tips**:
- Include "Use PROACTIVELY after..." or "MUST BE USED when..." for auto-triggering
- Be specific about the domain: "TypeScript type safety" not "code quality"
- State what it does NOT handle to prevent false triggers

---

## 2. Skills

**What they are**: Reusable packages of instructions, scripts, and resources that Claude auto-discovers and loads when relevant. Think of them as "prompt templates + bundled tools."

**Where they live**:
- Project: `.claude/skills/<skill-name>/SKILL.md`
- User: `~/.claude/skills/<skill-name>/SKILL.md`  
- User config dir: `~/.config/claude/skills/<skill-name>/SKILL.md`

**Directory structure**:
```
skill-name/
├── SKILL.md          # Required. Frontmatter + instructions
├── scripts/          # Optional. Executable code
├── references/       # Optional. Docs loaded as needed
└── assets/           # Optional. Templates, icons, fonts
```

**When to use**:
- Procedure that applies across many different prompts/contexts
- Knowledge that Claude should auto-load when it detects relevance
- Bundling deterministic scripts with natural language instructions
- Sharing capabilities across Claude Code, Claude.ai, and Claude Desktop

**When NOT to use**:
- One-time task (just tell Claude directly)
- Task that needs isolated context (use a subagent)
- User wants explicit control over when it triggers (use a slash command)

**Key difference from subagents**: Skills modify the CURRENT agent's context. Subagents create a NEW, isolated context. Skills are injected; subagents are delegated to.

**Frontmatter**:
```yaml
---
name: skill-name
description: "When to trigger and what it does. Be pushy — err on the side of triggering."
---
```

---

## 3. Slash Commands

**What they are**: User-invoked commands stored as Markdown files. Typed as `/command-name` in the terminal. Can orchestrate subagents, load skills, and define multi-step workflows.

**Where they live**:
- Project: `.claude/commands/<name>.md`
- User: `~/.claude/commands/<name>.md`

**When to use**:
- User wants to explicitly trigger a workflow (not auto-detect)
- Workflow is used regularly and benefits from quick invocation
- Orchestrating multiple subagents or steps in sequence
- Parameterized workflows (use `$ARGUMENTS`)

**Frontmatter**:
```yaml
---
description: What this command does
allowed-tools: Task, Read, Write, Bash  # Optional tool restriction
---
```

**Example — Research command that spawns parallel subagents**:
```markdown
---
description: Research a topic using parallel web + codebase agents
allowed-tools: Task, WebSearch, WebFetch, Grep, Glob, Read
---
# Research: $ARGUMENTS

Launch these subagents **in parallel**:
1. **Web Research Agent** — Search the web for relevant docs and discussions
2. **Codebase Agent** — Search the local codebase for related patterns
3. **Stack Overflow Agent** — Find community solutions

Synthesize all findings into a single report.
```

---

## 4. Hooks

**What they are**: Shell scripts or commands that run automatically in response to agent events. They intercept and can modify agent behavior.

**Where they live**: Configured in `.claude/settings.json` (project) or `~/.claude/settings.json` (user)

**Event types**:
- `PreToolUse` — Before a tool executes. Can block it (exit code 2).
- `PostToolUse` — After a tool returns. Can modify results.
- `Notification` — When the agent sends a notification.
- `Stop` — When the agent finishes.
- `SubagentStop` — When a subagent finishes.

**When to use**:
- Safety guardrails (block dangerous commands)
- Logging and auditing
- Notifications (desktop alerts, Slack messages)
- Auto-formatting or validation after edits
- Rate limiting external API calls

**Configuration example**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/hooks/validate-command.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/hooks/notify-complete.sh"
          }
        ]
      }
    ]
  }
}
```

**Hook exit codes**:
- `0` — Allow the operation
- `2` — Block the operation (error message fed back to Claude)
- Other — Treated as hook failure, operation proceeds

---

## 5. MCP Servers (Model Context Protocol)

**What they are**: Structured interfaces that connect Claude to external services, APIs, and data sources. They expose tools that Claude can call.

**Where they live**:
- Project-level: `.mcp.json` in the project root (recommended)
- User-level: `~/.claude/.mcp.json` (available across all projects)

**Transports**:
- `stdio` — Local process (most common for local tools)
- `sse` — Server-sent events (for remote servers)
- `streamable-http` — HTTP-based (newer, simpler remote transport)

**When to use**:
- Connecting to external APIs (GitHub, Jira, Slack, databases)
- Giving Claude access to services that require authentication
- Structured tool interfaces (vs. raw Bash commands)
- When you want tools to appear in Claude's tool list

**Configuration example** (`.mcp.json` in project root):
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

---

## 6. CLAUDE.md

**What it is**: A Markdown file that provides persistent context to Claude across all conversations in a project. It's the "project brain."

**Where it lives**:
- Project root: `CLAUDE.md` (main project context)
- Subdirectories: `CLAUDE.md` (scoped to that directory)
- User-level: `~/.claude/CLAUDE.md` (all projects)

**When to use**:
- Coding standards and conventions
- Architecture overview and key decisions
- Common patterns and anti-patterns for the project
- Agent coordination instructions ("when you see X, delegate to Y agent")
- Corrections from past mistakes ("Don't use library Z, it's deprecated")

**Best practices**:
- Keep it concise — every token counts against context
- Update it after correcting Claude ("Add this to CLAUDE.md so you remember")
- Use it for facts, not procedures (procedures belong in skills or commands)

---

## 7. Claude Agent SDK

**What it is**: A TypeScript/Python library for building agents programmatically. It's the engine behind Claude Code, exposed for developers.

**When to use**:
- Building production applications powered by Claude agents
- Embedding agents in CI/CD pipelines
- Custom UIs or interfaces for agent interactions
- When you need programmatic control over the agent lifecycle

**Key capabilities**:
- Define subagents in code (not just Markdown files)
- Custom tools beyond Claude Code's built-in set
- Hooks as callback functions (not just shell scripts)
- Session management and checkpointing
- Structured outputs
- Streaming responses

**Installation**:
```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk

# Python  
pip install claude-agent-sdk
```

**Basic usage** (TypeScript):
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Analyze the auth module for security issues",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Bash"],
    agents: [
      {
        name: "security-reviewer",
        description: "Reviews code for security vulnerabilities",
        tools: ["Read", "Grep", "Glob"],
        prompt: "You are a security expert..."
      }
    ]
  }
})) {
  console.log(message);
}
```

---

## Decision Tree: Which Primitive?

```
User's need
├── "I want Claude to automatically do X when it detects Y"
│   ├── During a tool call? → Hook (PreToolUse/PostToolUse)
│   ├── Based on conversation context? → Skill (auto-triggered by description)
│   └── Based on task type? → Subagent (auto-delegated by description)
│
├── "I want to explicitly trigger a workflow"
│   ├── Simple, one command? → Slash command
│   ├── Multi-step with delegation? → Slash command that spawns subagents
│   └── From code/CI? → Agent SDK
│
├── "I need to connect to an external service"
│   ├── Has an MCP server? → Use it
│   ├── Has a REST API? → Build an MCP server or use Bash + curl
│   └── Local tool/CLI? → Bash tool or custom MCP server
│
├── "I want Claude to remember X across conversations"
│   ├── Project facts/conventions? → CLAUDE.md
│   ├── Agent-specific knowledge? → Subagent with memory field
│   └── Reusable procedures? → Skill
│
└── "I'm building a production app"
    └── → Agent SDK (TypeScript or Python)
```
