<div align="center">

# 🏗️ Claude Agent Builder

### Turn any idea into production-ready AI agents in Claude Code

**Stop writing agent files from scratch.** Describe your problem → get researched, architected, production-ready agents, skills, hooks, and commands — automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://docs.anthropic.com/en/docs/claude-code/overview)
[![Agent SDK](https://img.shields.io/badge/Agent_SDK-Supported-orange)](https://docs.anthropic.com/en/docs/agents/claude-code-sdk-overview)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[**Quick Start**](#-quick-start) · [**How It Works**](#-how-it-works) · [**Examples**](#-real-world-examples) · [**Patterns**](#-architecture-patterns) · [**Contributing**](#-contributing)

</div>

---

## The Problem

Building agents in Claude Code means juggling **7 different primitives** (subagents, skills, hooks, commands, MCP servers, CLAUDE.md, Agent SDK), reading scattered docs, and starting from blank Markdown files every time.

**Claude Agent Builder fixes this.** It's a skill that acts as your personal agent architect — it interviews you, researches what already exists, designs the optimal system, and generates every file you need.

## ⚡ Quick Start

### macOS / Linux

```bash
git clone https://github.com/keysersoose/claude-agent-builder.git && cp -r claude-agent-builder/agent-builder ~/.claude/skills/
```

### Windows (PowerShell)

```powershell
git clone https://github.com/keysersoose/claude-agent-builder.git; Copy-Item -Recurse claude-agent-builder\agent-builder "$env:USERPROFILE\.claude\skills\agent-builder"
```

### Windows (CMD)

```cmd
git clone https://github.com/keysersoose/claude-agent-builder.git && xcopy /E /I claude-agent-builder\agent-builder "%USERPROFILE%\.claude\skills\agent-builder"
```

<details>
<summary>Other install methods</summary>

```bash
# macOS/Linux — install script
git clone https://github.com/keysersoose/claude-agent-builder.git
cd claude-agent-builder && ./install.sh

# macOS/Linux — project-level only
./install.sh --project
```

```powershell
# Windows — install script (PowerShell)
git clone https://github.com/keysersoose/claude-agent-builder.git
cd claude-agent-builder; .\install.ps1

# Windows — project-level only
.\install.ps1 -Project
```

```bash
# Any platform — project-level manual
git clone https://github.com/keysersoose/claude-agent-builder.git
cp -r claude-agent-builder/agent-builder .claude/skills/
```

</details>

Open Claude Code and say:

```
Build me an agent that reviews my PRs for security issues and posts comments on GitHub
```

The skill triggers automatically. That's it.

## 🧠 How It Works

Agent Builder operates in **6 phases**, adapting to how much context you provide:

```
  🔍 CONTEXT SCAN →  Reads your project files + conversation history automatically
  📋 DISCOVERY    →  Only asks what it can't figure out itself
  🌐 RESEARCH     →  Parallel search (GitHub + blogs + docs + community) → consolidated brief
  📐 ARCHITECTURE →  Proposes agents, gets your explicit approval before building
  🔨 BUILD        →  Writes all agent files directly into your project
  ✅ VERIFY       →  Self-checks everything, shows you what was built, asks for final OK
```

### Why not just ask Claude directly?

| Without Agent Builder | With Agent Builder |
|---|---|
| You need to know all 7 primitives | It picks the right ones for you |
| You write from blank `.md` files | It writes production-ready files directly into your project |
| You guess at descriptions and tools | It optimizes for auto-triggering |
| You explain your project from scratch | It scans your codebase and conversation history first |
| You don't know what exists already | It searches GitHub, blogs, docs, and community in parallel — then consolidates |
| Trial and error | Proposes → you approve → it builds → it verifies |

## 📦 What's Inside

```
agent-builder/
├── SKILL.md                       # Core skill — 6-phase agent building workflow
├── references/
│   ├── primitives-guide.md        # Complete guide to all Claude Code building blocks
│   └── agent-patterns.md          # 7 battle-tested multi-agent architecture patterns
└── scripts/
    ├── validate_agents.py         # Lint agent files for common issues
    └── scaffold_agent.py          # Generate starter files from templates
```

## 🗺️ Architecture Patterns

The skill knows **7 proven patterns** and selects the right one for your use case:

| Pattern | Best For | Example |
|---------|----------|---------|
| **Command → Agent → Skills** | Multi-step pipelines | Full-stack feature builder |
| **Research → Consolidate → Plan → Execute** | Understanding before acting | Codebase migration |
| **Parallel Specialists** | Independent analyses | Security + perf + style review |
| **Self-Evolving Agent** | Learning over time | Project onboarding guide |
| **Hook-Guarded Agent** | Safety-critical workflows | Read-only database analyst |
| **Slash Command + Handoff** | Quick entry → complex flow | Bug investigation |
| **MCP-Powered Agent** | External service integration | GitHub PR review bot |

## 🎯 Real-World Examples

**PR Security Reviewer** — subagent with GitHub MCP, PreToolUse safety hooks, slash command trigger, and persistent memory.

**Research Pipeline** — `/research` command spawning 3 parallel subagents (web, codebase, Stack Overflow) with synthesis and markdown report output.

**Self-Improving Onboarder** — subagent with `memory: project` that builds institutional knowledge across conversations.

See [`examples/`](examples/) for complete, ready-to-use configurations.

## 🔧 Utility Scripts

```bash
# Install dependency for validation script
pip install pyyaml

# Validate your agents for common issues
python agent-builder/scripts/validate_agents.py .claude/agents/

# Scaffold new agents from templates
python agent-builder/scripts/scaffold_agent.py my-agent .claude --type subagent
python agent-builder/scripts/scaffold_agent.py deploy-pipe .claude --type full-stack
```

> **Requirements**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) installed. Python 3.7+ for utility scripts.

## 🧩 Primitives Decision Tree

```
Your need
├── "Auto-do X when Y happens"
│   ├── During a tool call?           → Hook
│   ├── Based on context?             → Skill
│   └── Based on task type?           → Subagent
├── "Trigger a workflow"
│   ├── Simple command?               → Slash command
│   └── Multi-step?                   → Command + subagents
├── "Connect external services"       → MCP server
├── "Remember across conversations"   → CLAUDE.md / memory
└── "Production app"                  → Agent SDK
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

Add examples · Improve patterns · Enhance the skill · Fix bugs · Share feedback

## 📄 License

MIT — use it, modify it, share it. See [LICENSE](LICENSE).

---

<div align="center">

**Built by [keysersoose](https://github.com/keysersoose) · Powered by [Claude Code](https://code.claude.com)**

If this saved you time, **[give it a star](https://github.com/keysersoose/claude-agent-builder)**. It helps others find it.

<a href="https://star-history.com/#keysersoose/claude-agent-builder&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=keysersoose/claude-agent-builder&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=keysersoose/claude-agent-builder&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=keysersoose/claude-agent-builder&type=Date" width="600" />
 </picture>
</a>

</div>
