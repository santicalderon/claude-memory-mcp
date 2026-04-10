# claude-memory-mcp

An MCP server that gives Claude Code cross-session memory — persisted to a plain `.claude-memory.md` file inside your repo.

Each project gets its own memory. Commit the file to git and it follows the codebase forever.

## Install

```bash
# Via uvx (no install needed)
uvx claude-memory-mcp

# Or pip
pip install claude-memory-mcp
```

## Configure Claude Code

Add to your project's `.mcp.json` (or `~/.claude.json` for global):

```json
{
  "mcpServers": {
    "memory": {
      "command": "uvx",
      "args": ["claude-memory-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `memory_read(key)` | Read a stored value |
| `memory_write(key, value)` | Write a value |
| `memory_list()` | List all keys |

## How it works

Memory is stored as `## sections` in `.claude-memory.md` at your repo root:

```markdown
# Claude Memory

## architecture-decisions
We use SQLite for local dev and Postgres in prod.
Decided 2025-01-15 — migration too risky mid-sprint.

## current-sprint-context
Working on payment webhook handler. Stripe sends events
to /api/webhooks/stripe. See stripe_handler.py:42.
```

- **Project-scoped**: different repos = different memory files
- **Git-tracked**: commit `.claude-memory.md` — memory persists across machines and teammates
- **Human-readable**: open the file, edit it, diff it like any other source file
- **No auth, no cloud, no database**: just a file

## Use cases

- Remember architectural decisions across sessions
- Store "where I left off" context so Claude doesn't ask again
- Share team conventions without repeating them in every prompt
- Track ongoing debugging context across long refactors

## Show HN post

> **Show HN: I built an MCP server that gives Claude Code a persistent memory file**
>
> The problem: every Claude Code session starts fresh. I keep explaining the same architectural decisions, the same "don't touch X" rules, the same "we use Y for Z" conventions.
>
> This MCP server persists memory to `.claude-memory.md` — a plain markdown file in your repo. Claude reads and writes it across sessions. Commit it to git and it follows the codebase.
>
> Three tools: `memory_read`, `memory_write`, `memory_list`. That's it.
>
> Install: add 8 lines to your `.mcp.json`, run `uvx claude-memory-mcp`.
>
> Source: [github.com/santicalderon/claude-memory-mcp](https://github.com/santicalderon/claude-memory-mcp)

## License

MIT
