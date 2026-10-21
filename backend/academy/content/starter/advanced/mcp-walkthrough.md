# Working MCP server and client over stdio

## Learn the concept

This exercise launches an actual SDK server subprocess. The client discovers a tool, calls it, reads a resource, rejects invalid input and closes the subprocess. A Python function decorated as a tool is only one part of the server; the client/server transport test below proves the local protocol path works.

The tested example uses MCP Python SDK **1.30.0**, with FastMCP, ClientSession, explicit initialize and camelCase isError fields. Use the pinned environment rather than mixing incompatible APIs. The server exposes a fixed synthetic collection; no production login or multi-tenant authorization is claimed.
## Step 1 — Prepare a separate exercise folder

Download the program starter kit from the Accelerator overview. Extract the ZIP and open `workspace/advanced` in your terminal. Do not run these commands inside Workshop's application folder. Python 3.12 works on your Intel Mac; there is no GPU or paid API requirement.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The dependency file pins the tested MCP and LangGraph releases. This is a separate environment, not an upgrade of Workshop. If `python3.12` is unavailable, locate your installed Python 3.12 interpreter and use its absolute path. If importing `mcp` fails, check `python -m pip show mcp` and ensure the same interpreter runs your script.
## Step 2 — Create the shared evidence module

Our collection contains two synthetic policies. `search` validates input and returns IDs with evidence. Lexical matching is deliberately simple: it teaches the orchestration boundary, not advanced RAG relevance. Returned text is data, never an instruction to expand tool permissions.

Save as `policies.py` (complete file):

```python
"""Synthetic, allowlisted evidence. No files, network or user database access."""
POLICIES = {"policy-1": "Refund requests must be submitted within 30 days.",
            "policy-2": "Support is available Monday through Friday."}

def search(query: str) -> list[dict[str, str]]:
    if not isinstance(query, str) or not 3 <= len(query) <= 200:
        raise ValueError("query must contain 3..200 characters")
    words = set(query.lower().split())
    return [{"id": key, "text": text} for key, text in POLICIES.items()
            if words & set(text.lower().replace(".", "").split())]
```
## Step 3 — Create the server

The SDK derives the tool schema from type hints. ToolError reports an expected input error without an unexpected-exception traceback. The function still checks application constraints: a string of the wrong length must fail. The resource URI is allowlisted and does not become an arbitrary file path. Logging goes to stderr; stdout belongs to the JSON-RPC transport.

Save as `mcp_server.py` (complete file):

```python
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
```
## Step 4 — Create the client

The client uses `sys.executable`, so its subprocess uses the same virtual environment. The script resolves the server path from its own location and closes the process through the async context manager. Tool discovery must return exactly the expected tool before we invoke it. The SDK wraps array output, so the example inspects returned text without inventing a wrapper key.

Save as `mcp_client.py` (complete file):

```python
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
```
## Step 5 — Run the transport test

```bash
python mcp_client.py
```

You do not need to start the server separately; the client launches it. Expect `Discovered: search_policies`, then `Policy call: PASS; resource read: PASS; invalid query: rejected`, a negotiated protocol value, and `Server subprocess closed.` Informational SDK messages may appear on stderr. The client has a 20-second timeout so a broken subprocess does not hang indefinitely.

Running `python mcp_server.py` alone waits for protocol input and can look idle; use the client to test it, or stop the manual server with Ctrl-C. No browser or API key is needed.

## Step 6 — Investigate protocol and tool failures

Temporarily add `print("debug")` before server startup. It writes to stdout and can corrupt the transport. Remove it and use `logging.info("debug")` instead. Change the client query to an empty string: the server should return a tool error, not successful empty evidence. Remove the resource and see the resource-read assertion fail. Restore each change before moving on.

## Step 7 — Extend carefully

Add a second fixed resource for support hours and a client assertion. Keep resource IDs and tool names explicit. Do not expose arbitrary file reads or reuse model arguments as caller identity. Network transport, authentication, cancellation and deployment require additional exercises; passing this local stdio test establishes only this local integration.

## Acceptance checks

Explain host, client, server, tool and resource in your own words. Show where discovery, validation and cleanup happen. The deterministic caller does not use an LLM; connecting a model to discovered tools is an optional next adapter exercise after the boundary works.

## References

[Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [SDK client documentation](https://py.sdk.modelcontextprotocol.io/client/) · [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview).
