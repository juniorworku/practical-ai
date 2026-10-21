"""A real stdio MCP server; the service owns fixture identity, never the tool caller."""
import os
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from agent import search
server=FastMCP('Capstone scoped policy search')
DOCUMENT=os.environ['CAPSTONE_DOCUMENT_ID']
@server.tool()
def search_policies(query:str)->dict:
 if not 3<=len(query.strip())<=200:raise ToolError('query_3_to_200_characters')
 try:return search(DOCUMENT,query)
 except (RuntimeError,OSError):raise ToolError('policy_service_unavailable') from None
if __name__=='__main__':server.run(transport='stdio')
