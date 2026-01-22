import asyncio 
from aiohttp import web, WSMsgType, ClientSession 
import json 
import os 
import base64 
import random 
 
MOCK_TRANSCRIPTIONS = [ 
    "I would like to book an appointment", 
    "I need to see the doctor", 
    "What time is available tomorrow", 
    "Is Dr. Ntombela available on Friday", 
    "Can I book for next week", 
    "I need a checkup" 
] 
 
async def transcribe_isizulu_audio(audio_data): 
    print(f"Received audio: {len(audio_data)} bytes") 
    transcription = random.choice(MOCK_TRANSCRIPTIONS) 
    print(f"Mock transcription: {transcription}") 
    return transcription 
 
async def websocket_handler(request): 
    print("New WebSocket connection attempt") 
    ws = web.WebSocketResponse() 
    await ws.prepare(request) 
    print("Vapi connected!") 
 
    session_config = { 
        "type": "session", 
        "session": { 
            "id": "tameeka_session", 
            "language": "zul" 
        } 
    } 
    await ws.send_str(json.dumps(session_config)) 
    print("Sent session configuration") 
 
    try: 
        async for msg in ws: 
            if msg.type == WSMsgType.TEXT: 
                try: 
                    data = json.loads(msg.data) 
                    print(f"Received text message: {data}") 
                except: 
                    print(f"Received raw text: {msg.data}") 
            elif msg.type == WSMsgType.BINARY: 
                transcription = await transcribe_isizulu_audio(msg.data) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                print(f"Sending transcription: {transcription}") 
                await ws.send_str(json.dumps(response)) 
            elif msg.type == WSMsgType.CLOSE: 
                print("WebSocket closed by client") 
                break 
            elif msg.type == WSMsgType.ERROR: 
                print(f"WebSocket error: {ws.exception()}") 
    except Exception as e: 
        print(f"Error in WebSocket: {e}") 
    finally: 
        print("Vapi disconnected") 
        await ws.close() 
    return ws 
 
async def health_check(request): 
    return web.Response( 
        text=json.dumps({ 
            "status": "online", 
            "service": "Tameeka IsiZulu Bridge", 
            "language": "isiZulu (zul)", 
            "active_connections": 0 
        }), 
        content_type='application/json' 
    ) 
 
app = web.Application() 
app.router.add_get('/ws', websocket_handler) 
app.router.add_get('/', health_check) 
 
if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 8000)) 
    print(f"Starting server on port {port}") 
    web.run_app(app, port=port, host='0.0.0.0') 
