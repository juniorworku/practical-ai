"""Run beside mcp_policy.py after installing the supplied dependencies."""
import asyncio, sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).with_name('mcp_policy.py'))])
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()
            tools=await session.list_tools()
            assert [t.name for t in tools.tools]==['lookup_policy']
            result=await session.call_tool('lookup_policy',{'policy_id':'returns-v1'})
            assert not result.isError
            assert '14 days' in result.content[0].text
            print(result.model_dump_json())
asyncio.run(main())
