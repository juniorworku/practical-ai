"""Run a true ingestion -> persisted retrieval -> agent -> MCP round trip."""
import asyncio,json,os,sys,time
from pathlib import Path
from agent import request,run
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

def prepare():
 row=request('POST','/documents',{'text':'Refund policy is 14 days for unopened items. Capstone source.'})
 for _ in range(40):
  if request('GET','/documents/'+row['id'])['state']=='ready':return row['id']
  time.sleep(.2)
 raise AssertionError('worker did not make document ready')

async def protocol(document):
 environment={**os.environ,'CAPSTONE_DOCUMENT_ID':document}
 params=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).with_name('mcp_server.py').resolve())],env=environment)
 async with stdio_client(params) as (read,write):
  async with ClientSession(read,write) as client:
   await client.initialize();tools=await client.list_tools()
   assert [tool.name for tool in tools.tools]==['search_policies']
   called=await client.call_tool('search_policies',{'query':'refund'})
   assert not called.isError
   text='\n'.join(b.text for b in called.content if b.type=='text')
   data=json.loads(text);assert '14 days' in data['answer'] and all(c.startswith(document+':') for c in data['citations'])
   invalid=await client.call_tool('search_policies',{'query':' '});assert invalid.isError
   denied=await client.call_tool('delete',{});assert denied.isError
 return {'actual_stdio_discovery':True,'actual_persisted_source_call':True,'invalid_query_rejected':True,'unknown_write_tool_rejected':True}

if __name__=='__main__':
 document=prepare();normal=run(document,'refund policy');assert normal['status']=='completed' and '14 days' in normal['answer']
 assert run(document,'unicorn wallpaper')['status']=='abstained'
 assert run(document,'refund',lambda observations:{'name':'delete'})['status']=='denied_action'
 assert run(document,'refund',lambda observations:{'name':'finish'})['status']=='missing_evidence'
 assert run(document,'refund',lambda observations:{'name':'search'},max_steps=1)['status']=='step_budget'
 bad=run('nonexistent','refund');assert bad['status']=='service_unavailable'
 result=asyncio.run(asyncio.wait_for(protocol(document),timeout=30))
 report={'document_id':document,'agent':normal,'checks':result,'mode':'scripted_agent_real_http_pg_worker_and_mcp','external_side_effects':False}
 Path('observed-agent.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
