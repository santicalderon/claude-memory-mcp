#!/usr/bin/env python3
"""claude-memory-mcp — persists Claude Code memory to a git-tracked file.

Each key is stored as a ## section in .claude-memory.md in the current repo root.
Commit that file with your project — memory follows the repo, not the machine.
"""

import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

MEMORY_FILE = ".claude-memory.md"

server = Server("claude-memory-mcp")


def _path() -> Path:
    return Path.cwd() / MEMORY_FILE


def _load() -> dict[str, str]:
    """Parse ## sections from .claude-memory.md into {key: value}."""
    p = _path()
    if not p.exists():
        return {}
    sections: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if key is not None:
                sections[key] = "\n".join(buf).strip()
            key = line[3:].strip()
            buf = []
        elif key is not None:
            buf.append(line)
    if key is not None:
        sections[key] = "\n".join(buf).strip()
    return sections


def _save(sections: dict[str, str]) -> None:
    """Write {key: value} back to .claude-memory.md."""
    chunks = ["# Claude Memory\n\n"]
    for k, v in sections.items():
        chunks.append(f"## {k}\n{v}\n\n")
    _path().write_text("".join(chunks), encoding="utf-8")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="memory_read",
            description=(
                "Read a value from Claude's persistent project memory. "
                "Returns the stored value or a 'not found' message."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Memory key to read"}
                },
                "required": ["key"],
            },
        ),
        Tool(
            name="memory_write",
            description=(
                "Write a value to Claude's persistent project memory. "
                "Persisted to .claude-memory.md — commit it to git."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Memory key"},
                    "value": {"type": "string", "description": "Value to store"},
                },
                "required": ["key", "value"],
            },
        ),
        Tool(
            name="memory_list",
            description="List all keys currently stored in this project's memory.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    sections = _load()

    if name == "memory_read":
        key = arguments["key"]
        value = sections.get(key)
        if value is None:
            return [TextContent(type="text", text=f"(no memory for key: {key})")]
        return [TextContent(type="text", text=value)]

    if name == "memory_write":
        key = arguments["key"]
        value = arguments["value"]
        sections[key] = value
        _save(sections)
        return [TextContent(type="text", text=f"✓ Saved '{key}' to {MEMORY_FILE}")]

    if name == "memory_list":
        if not sections:
            return [TextContent(type="text", text="Memory is empty.")]
        lines = "\n".join(f"- {k}" for k in sorted(sections))
        return [TextContent(type="text", text=f"Keys in {MEMORY_FILE}:\n{lines}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _main() -> None:
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())


def run() -> None:
    asyncio.run(_main())
