"""Local stdio MCP teaching server; server-scoped single synthetic tenant.
Register: command python, arguments absolute path to this file.
No credentials, no arbitrary filesystem tool, no messaging effects.
"""
from mcp.server.fastmcp import FastMCP
server=FastMCP('Synthetic policy reader')
POLICIES={'returns-v1':'Unopened items within 14 days; opened items excluded.'}
@server.tool()
def lookup_policy(policy_id:str)->dict:
    """Read an allowlisted synthetic policy; no writes or filesystem paths."""
    if policy_id not in POLICIES:return {'status':'not_found'}
    return {'status':'found','id':policy_id,'text':POLICIES[policy_id]}
if __name__=='__main__':server.run(transport='stdio')
