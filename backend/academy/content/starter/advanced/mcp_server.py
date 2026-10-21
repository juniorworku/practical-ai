"""Local stdio MCP server. All protocol stdout is owned by the SDK."""
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from policies import search, POLICIES
logging.basicConfig(level=logging.INFO)  # stderr by default
server = FastMCP("Workshop policy exercise")

@server.tool()
def search_policies(query: str) -> list[dict[str, str]]:
    """Search the fixed synthetic policy collection; returns IDs and evidence."""
    try:
        return search(query)
    except ValueError as error:
        raise ToolError(str(error)) from error

@server.resource("policy://refund")
def refund_policy() -> str:
    return POLICIES["policy-1"]

if __name__ == "__main__":
    server.run(transport="stdio")
