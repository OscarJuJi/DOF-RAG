"""Verify a real MCP handshake, API access, local search, and origin protection."""

import argparse
import asyncio
import sys

import httpx
from mcp.client.stdio import StdioServerParameters

from mcp import Client


async def main(url: str, stdio: bool = False):
    target = (
        StdioServerParameters(command=sys.executable, args=["-m", "dof_mcp.server"])
        if stdio
        else url
    )
    async with Client(target, raise_exceptions=True) as client:
        available = await client.list_tools()
        names = {tool.name for tool in available.tools}
        assert len(names) == 7, names
        result = await client.call_tool(
            "dof_list_editions", {"publication_date": "2024-01-02"}
        )
        editions = result.structured_content
        assert editions["editions"][0]["id"] == 310661, editions
        result = await client.call_tool(
            "dof_get_note", {"note_id": 5713405, "max_chars": 100}
        )
        note = result.structured_content
        assert note["has_text"] and note["next_offset"] == 100, note
        result = await client.call_tool(
            "dof_archive_search",
            {
                "query": "protección ambiental",
                "start_date": "2024-01-02",
                "end_date": "2024-01-02",
            },
        )
        assert result.structured_content["items"], result
        result = await client.call_tool(
            "dof_archive_read", {"edition_id": 310661, "max_chars": 80}
        )
        assert len(result.structured_content["text"]) == 80, result
        result = await client.call_tool("dof_archive_status", {})
        status = result.structured_content
        print(
            {
                "tools": sorted(names),
                "archive": status["totals"],
                "run": status["latest_run"]["status"],
            }
        )
    response = httpx.post(
        url,
        headers={"Host": "attacker.invalid", "Origin": "http://attacker.invalid"},
        json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
    )
    assert response.status_code in (400, 403, 421), response.status_code
    response = httpx.post(
        url,
        headers={
            "Origin": "http://attacker.invalid",
            "Accept": "application/json, text/event-stream",
        },
        json={"jsonrpc": "2.0", "id": 2, "method": "ping"},
    )
    assert response.status_code == 403, response.status_code
    print(
        "MCP handshake, live DOF API, local search, pagination and origin checks passed."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://dof-mcp:8001/mcp")
    parser.add_argument("--stdio", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.url, args.stdio))
