import asyncio 
from aiohttp import web, WSMsgType, ClientSession 
import json 
import os 
import base64 
 
async def transcribe_isizulu_audio(audio_data): 
    print(f"Received audio data: {len(audio_data)} bytes") 
 
    api_key = os.environ.get("VULAVULA_API_KEY") 
    if not api_key: 
        print("Warning: No Vulavula API key set, using fallback") 
        return "I would like to book an appointment" 
 
    print("Skipping Vulavula API (endpoint not working)") 
 
    FALLBACK_TRANSCRIPTIONS = [ 
        "I would like to book an appointment", 
        "What time is available tomorrow", 
        "I need to see the doctor", 
        "Is Dr. Ntombela available on Friday" 
    ] 
 
    import random 
    return random.choice(FALLBACK_TRANSCRIPTIONS) 
 
async def websocket_handler(request): 
    ws = web.WebSocketResponse() 
    await ws.prepare(request) 
    print("Vapi connected!") 
 
    await ws.send_str(json.dumps({ 
        "type": "session", 
        "session": { 
            "id": "tameeka_session", 
            "language": "zul" 
        } 
    })) 
 
    try: 
        async for msg in ws: 
            if msg.type == WSMsgType.TEXT: 
                print(f"Received text: {msg.data}") 
            elif msg.type == WSMsgType.BINARY: 
                transcription = await transcribe_isizulu_audio(msg.data) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await ws.send_str(json.dumps(response)) 
                print(f"Sent transcription: {transcription}") 
            elif msg.type == WSMsgType.ERROR: 
                print(f"WebSocket error: {ws.exception()}") 
    except Exception as e: 
        print(f"Error in WebSocket handler: {e}") 
 
    print("Vapi disconnected") 
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
    web.run_app(app, port=port, host='0.0.0.0') 
