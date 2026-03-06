# Agent Architecture Patterns

Battle-tested patterns for building multi-agent systems in Claude Code. Each pattern includes when to use it, the file structure, and complete working examples.

---

## Pattern 1: Command → Agent → Skills (Orchestrated Pipeline)

**When to use**: Multi-step workflows where the user explicitly triggers a pipeline that delegates to specialized agents, each with their own skills.

**How it works**: A slash command acts as the entry point. It spawns one or more subagents. Each subagent can auto-load skills that give it domain expertise.

**Example — Full-Stack Feature Builder**:

```
.claude/
├── commands/
│   └── build-feature.md          # Entry point
├── agents/
│   ├── feature-planner.md        # Plans the implementation
│   ├── backend-dev.md            # Builds backend code
│   ├── frontend-dev.md           # Builds frontend code
│   └── qa-reviewer.md            # Reviews everything
└── skills/
    ├── api-patterns/
    │   └── SKILL.md              # REST API conventions
    └── component-patterns/
        └── SKILL.md              # React component patterns
```

**Slash command** (`build-feature.md`):
```markdown
---
description: Build a full-stack feature from a description
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob
---
# Build Feature: $ARGUMENTS

## Step 1: Plan
Use the **feature-planner** subagent to analyze the codebase and create an implementation plan.

## Step 2: Build (Parallel)
Launch **backend-dev** and **frontend-dev** subagents IN PARALLEL:
- Backend: Implement the API endpoints and data layer
- Frontend: Build the UI components and state management

## Step 3: Review
Use the **qa-reviewer** subagent to review all changes for quality, consistency, and test coverage.

## Step 4: Report
Summarize what was built, what tests were added, and any manual steps needed.
```

---

## Pattern 2: Research → Consolidate → Plan → Execute

**When to use**: Tasks that require understanding before action. The agent first explores (in parallel), consolidates findings, then plans, then implements.

**How it works**: Multiple explore-phase subagents (read-only, fast) gather context in parallel across different sources. A consolidation step cross-references results, removes outdated info, and ranks by source reliability. Then a planning step synthesizes the consolidated findings. Finally, execution happens with full tool access.

**Example — Codebase Migration Agent**:

```
.claude/agents/
├── migration-researcher.md   # Read-only exploration
└── migration-executor.md     # Full tool access for changes
```

**Researcher** (`migration-researcher.md`):
```markdown
---
name: migration-researcher
description: Research codebase for migration planning. Read-only analysis.
tools: Read, Grep, Glob, Bash
model: haiku
---
You are a migration analyst. Your job is to thoroughly understand the current state of the codebase before any changes are made.

When invoked:
1. Search for all files affected by the migration
2. Map dependencies between affected modules
3. Identify patterns currently in use
4. Flag potential breaking changes
5. Return a structured report (NOT code changes)

Important: You are read-only. Do NOT suggest edits. Only analyze and report.
```

---

## Pattern 3: Parallel Specialists

**When to use**: A problem has multiple independent dimensions that can be analyzed simultaneously.

**How it works**: Multiple subagents are spawned in the same turn. Each tackles a different aspect. The main agent synthesizes results.

**Example — Comprehensive Code Review**:
```
.claude/agents/
├── security-reviewer.md      # Security vulnerabilities
├── performance-reviewer.md   # Performance bottlenecks
├── style-reviewer.md         # Code style and readability
└── test-reviewer.md          # Test coverage gaps
```

Invoke all four in parallel:
```
Review my recent changes using ALL review agents in parallel:
- security-reviewer for vulnerability analysis
- performance-reviewer for bottleneck detection
- style-reviewer for readability
- test-reviewer for coverage gaps
Then combine findings into a single prioritized report.
```

---

## Pattern 4: Self-Evolving Agent (Memory + Skills)

**When to use**: An agent that should get smarter over time by recording what it learns.

**How it works**: The agent has the `memory` field set, giving it a persistent directory. After completing tasks, it writes notes about patterns, decisions, and lessons learned.

**Example — Project Onboarding Agent**:
```markdown
---
name: onboarding-guide
description: Helps new team members understand the codebase. Gets smarter with each interaction.
memory: project
skills: codebase-map
---
You are a project guide that helps developers understand this codebase.

## Memory Management
You have a persistent memory directory. Use it to build knowledge:

After EVERY interaction:
1. Check if you learned something new about the codebase
2. If yes, update your memory with a concise note:
   - File: `patterns/<topic>.md` for recurring patterns
   - File: `gotchas/<topic>.md` for common pitfalls
   - File: `architecture/<component>.md` for architectural knowledge

Before answering questions:
1. Check your memory for relevant notes
2. Use stored knowledge to give more accurate, project-specific answers

This builds institutional knowledge across conversations.
```

---

## Pattern 5: Hook-Guarded Agent (Safety-Critical Workflows)

**When to use**: When the agent has powerful tools but needs guardrails to prevent dangerous operations.

**How it works**: PreToolUse hooks validate operations before they execute. The hook script receives the tool input as JSON via stdin and can block the operation.

**Example — Database Agent with Read-Only Guard**:

**Agent** (`db-analyst.md`):
```markdown
---
name: db-analyst
description: Analyze database queries and suggest optimizations. Use for any database-related tasks.
tools: Bash, Read, Grep
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/hooks/validate-db-query.sh"
---
You are a database analyst. You can run SQL queries to analyze data patterns, but all queries are validated for safety before execution.

If a query is blocked by the safety check, explain why and suggest a safe alternative.
```

**Hook script** (`scripts/hooks/validate-db-query.sh`):
```bash
#!/bin/bash
# Read the tool input from stdin
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block destructive SQL operations
if echo "$COMMAND" | grep -iE '(DROP|DELETE|TRUNCATE|ALTER|INSERT|UPDATE|CREATE)' | grep -ivE '(CREATE TEMP|CREATE TEMPORARY)'; then
  echo "BLOCKED: Only SELECT and read-only queries are allowed. Detected write operation."
  exit 2
fi

exit 0
```

---

## Pattern 6: Slash Command + Subagent Handoff

**When to use**: When you want a quick entry point that gathers info from the user, then hands off to a specialized agent.

**Example — Bug Investigation Flow**:

**Slash command** (`investigate-bug.md`):
```markdown
---
description: Investigate a bug report by gathering context and running analysis
allowed-tools: Task, Read, Grep, Glob, Bash, WebSearch
---
# Investigate Bug: $ARGUMENTS

## Step 1: Gather Context
Ask the user (if not already provided):
- Error message or stack trace
- Steps to reproduce
- When it started happening
- Any recent changes that might be related

## Step 2: Delegate to Debugger
Use the **debugger** subagent with all gathered context to:
1. Locate the root cause
2. Propose a fix
3. Verify the fix doesn't break anything

## Step 3: Summary
Present the findings with:
- Root cause explanation
- Proposed fix (as a diff)
- Risk assessment
- Recommended tests to add
```

---

## Pattern 7: MCP-Powered Agent (External Service Integration)

**When to use**: The agent needs to interact with external services (GitHub, Jira, Slack, databases, APIs).

**How it works**: MCP servers expose external services as tools. The agent uses these tools naturally alongside Claude Code's built-in tools.

**Example — PR Review Bot**:

**MCP config** (`.mcp.json` in project root):
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Agent** (`pr-reviewer.md`):
```markdown
---
name: pr-reviewer
description: Reviews pull requests on GitHub. Use when asked to review PRs or when PR URLs are mentioned.
tools: Read, Grep, Glob, Bash, mcp__github__*
model: sonnet
---
You are a pull request reviewer with access to GitHub via MCP.

When reviewing a PR:
1. Fetch the PR details and diff using GitHub MCP tools
2. Read the affected files in the local codebase for context
3. Analyze changes for quality, security, and test coverage
4. Post your review as a GitHub comment using the MCP tools

Keep reviews constructive and specific. Include code suggestions where appropriate.
```

---

## Choosing a Pattern

| Scenario | Best Pattern |
|----------|-------------|
| Multi-step workflow, user-triggered | Command → Agent → Skills |
| Need to understand before acting | Research → Consolidate → Plan → Execute |
| Multiple independent analyses | Parallel Specialists |
| Agent should learn over time | Self-Evolving (Memory) |
| Dangerous tools need guardrails | Hook-Guarded |
| Quick entry to complex flow | Slash Command + Handoff |
| External service integration | MCP-Powered |
| Production app embedding | Agent SDK (see primitives guide) |

Many real-world systems combine multiple patterns. A PR review agent might use **MCP-Powered** (GitHub access) + **Parallel Specialists** (security + style + tests) + **Hook-Guarded** (prevent accidental merges).
