"""Launch a real MCP subprocess, discover and call its tool, then close it."""
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def exercise():
    server_path = Path(__file__).with_name("mcp_server.py").resolve()
    params = StdioServerParameters(command=sys.executable, args=[str(server_path)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            initialized = await client.initialize()
            tools = await client.list_tools()
            assert [tool.name for tool in tools.tools] == ["search_policies"]
            result = await client.call_tool("search_policies", {"query": "refund requests"})
            assert not result.isError
            # Array return is wrapped by the SDK; inspect text without assuming a wrapper name.
            text = "\n".join(block.text for block in result.content if block.type == "text")
            assert "policy-1" in text and "30 days" in text
            resource = await client.read_resource("policy://refund")
            assert "30 days" in resource.contents[0].text
            invalid = await client.call_tool("search_policies", {"query": ""})
            assert invalid.isError
            print("Discovered:", tools.tools[0].name)
            print("Policy call: PASS; resource read: PASS; invalid query: rejected")
            print("Negotiated protocol:", initialized.protocolVersion)
    print("Server subprocess closed.")

if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(exercise(), timeout=20))
