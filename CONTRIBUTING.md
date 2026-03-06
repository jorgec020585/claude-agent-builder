# Contributing to Claude Agent Builder

Thanks for your interest in contributing! This project is open to everyone — whether you're a Claude Code power user or just getting started.

## Ways to Contribute

### Share Your Agent Builds
Built something cool with this skill? Open a [Discussion](https://github.com/keysersoose/claude-agent-builder/discussions) and share it! We love seeing what people create.

### Report Issues
Found a bug or have a suggestion? [Open an issue](https://github.com/keysersoose/claude-agent-builder/issues/new/choose) using one of our templates.

### Submit Pull Requests

**Good first contributions:**
- Add a new architecture pattern to `references/agent-patterns.md`
- Improve validation checks in `scripts/validate_agents.py`
- Add new scaffold templates in `scripts/scaffold_agent.py`
- Fix typos or improve documentation
- Add example agent configs in `examples/`

**How to submit:**
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Make your changes
4. Test that the skill still works in Claude Code
5. Commit with a clear message (`git commit -m "Add: new pattern for X"`)
6. Push and open a PR

### Code Style
- Markdown files: Use ATX-style headers (`#`, `##`, `###`)
- Python scripts: Follow PEP 8
- YAML frontmatter: Use lowercase keys with hyphens
- Keep SKILL.md under 500 lines (use reference files for overflow)

### Testing Your Changes
1. Copy the modified `agent-builder/` to `~/.claude/skills/`
2. Open Claude Code and try prompts like:
   - "Build me a code review agent"
   - "I need an agent that deploys my app"
   - "Create a research agent with web search"
3. Verify the skill triggers and produces reasonable output

## Code of Conduct

Be kind. Be constructive. We're all here to build cool stuff.
