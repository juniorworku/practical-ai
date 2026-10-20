"""Loopback teaching gateway. Offline PCM echo by default; Gemini is opt-in.
Run: uvicorn voice_gateway:app --host 127.0.0.1 --port 8092
Set VOICE_LAB_TOKEN; for live use also VOICE_MODE=gemini, GOOGLE_API_KEY,
and GEMINI_LIVE_MODEL (a currently available audio-output Live model).
"""
import asyncio
import contextlib
import os
from pathlib import Path
import secrets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app=FastAPI()
slots=asyncio.Semaphore(4)  # Process-local lab guard; use shared quotas across replicas.
ROOT=Path(__file__).resolve().parent

@app.get('/')
def index():return FileResponse(ROOT/'voice.html')

@app.get('/health')
def health():return {'gateway':'ready','mode':os.getenv('VOICE_MODE','echo'),'provider_tested':False}

async def echo(ws):
    import json
    total=0
    while True:
        event=await ws.receive()
        if event['type']=='websocket.disconnect':return
        if event.get('bytes') is not None:
            data=event['bytes'];total+=len(data)
            if len(data)>6400 or len(data)%2 or total>1_920_000:raise ValueError('invalid PCM frame or session budget')
            await ws.send_json({'type':'audio_format','rate':16000,'fixture':True})
            await ws.send_bytes(data)  # Transport only, not AI inference.
        elif event.get('text'):
            if json.loads(event['text']).get('type')!='audio_end':raise ValueError('unsupported echo event')
            await ws.send_json({'type':'audio_stopped','fixture':True})

async def gemini(ws):
    from google import genai
    from google.genai import types
    key=os.environ['GOOGLE_API_KEY'];model=os.environ['GEMINI_LIVE_MODEL']
    client=genai.Client(api_key=key)
    config={'response_modalities':['AUDIO']}
    async with client.aio.live.connect(model=model,config=config) as session:
        async def send():
            total_bytes=0
            while True:
                event=await ws.receive()
                if event['type']=='websocket.disconnect':return
                if event.get('bytes') is not None:
                    data=event['bytes'];total_bytes+=len(data)
                    if len(data)>6400 or len(data)%2 or total_bytes>1_920_000:
                        raise ValueError('audio frame or session budget exceeded')
                    await session.send_realtime_input(audio=types.Blob(data=data,mime_type='audio/pcm;rate=16000'))
                elif event.get('text'):
                    import json
                    message=json.loads(event['text'])
                    if message.get('type')=='audio_end':
                        await session.send_realtime_input(audio_stream_end=True)
                    elif message.get('type')=='text' and type(message.get('text')) is str and len(message['text'])<=1000:
                        await session.send_client_content(turns=types.Content(role='user',parts=[types.Part(text=message['text'])]),turn_complete=True)
                    else:raise ValueError('unsupported event')
        async def receive():
            while True:  # receive() may end at a turn boundary; keep the session alive.
                async for response in session.receive():
                    content=response.server_content
                    if content and content.interrupted:
                        await ws.send_json({'type':'interrupted'})
                    if content and content.model_turn:
                        for part in content.model_turn.parts:
                            if part.inline_data and part.inline_data.data:
                                await ws.send_json({'type':'audio_format','rate':24000,'fixture':False})
                                await ws.send_bytes(part.inline_data.data)
                            if part.text:await ws.send_json({'type':'text','text':part.text})
                    if response.usage_metadata:
                        await ws.send_json({'type':'usage','data':response.usage_metadata.model_dump(mode='json')})
        tasks=[asyncio.create_task(send()),asyncio.create_task(receive())]
        try:
            done,_=await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
            for task in done:task.result()
        finally:
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)

@app.websocket('/voice')
async def voice(ws:WebSocket):
    allowed={'http://127.0.0.1:8092','http://localhost:8092'}
    if ws.headers.get('origin') not in allowed:
        await ws.close(code=1008);return
    await ws.accept()
    try:
        async with asyncio.timeout(5):auth=await ws.receive_json()
        token=os.environ.get('VOICE_LAB_TOKEN','')
        if not token or type(auth.get('token')) is not str or not secrets.compare_digest(auth['token'],token):
            await ws.close(code=1008);return
        if slots.locked():
            await ws.send_json({'type':'error','code':'capacity_exceeded'});await ws.close(code=1013);return
        async with slots:
            await ws.send_json({'type':'ready','mode':os.getenv('VOICE_MODE','echo'),'session_seconds':60})
            async with asyncio.timeout(60):
                if os.getenv('VOICE_MODE','echo')=='gemini':await gemini(ws)
                else:await echo(ws)
    except WebSocketDisconnect:pass
    except Exception:
        # Stable public category; no API keys/raw exceptions in client responses.
        with contextlib.suppress(Exception):await ws.send_json({'type':'error','code':'session_ended_or_provider_unavailable'})
    finally:
        with contextlib.suppress(Exception):await ws.close()
