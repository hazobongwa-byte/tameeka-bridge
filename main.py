from aiohttp import web, WSMsgType, ClientSession 
import json 
import os 
import base64 
 
VULAVULA_API_KEY = os.environ.get("VULAVULA_API_KEY") 
VULAVULA_API_URL = "https://api.lelapa.ai/vulavula/transcribe" 
 
async def transcribe_isizulu_audio(audio_data): 
    if not VULAVULA_API_KEY: 
        print("Vulavula API key not set") 
        return "I would like to book an appointment" 
 
    async with ClientSession() as session: 
        headers = { 
            "Authorization": f"Bearer {VULAVULA_API_KEY}", 
            "Content-Type": "application/json" 
        } 
 
        audio_base64 = base64.b64encode(audio_data).decode('utf-8') 
 
        payload = { 
            "audio": audio_base64, 
            "language": "zul", 
            "format": "wav" 
        } 
 
        try: 
            async with session.post(VULAVULA_API_URL, json=payload, headers=headers) as response: 
                result = await response.json() 
                return result.get("transcription", "I would like to book an appointment") 
        except Exception as e: 
            print(f"Vulavula API error: {e}") 
            return "I would like to book an appointment" 
 
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
 
    async for msg in ws: 
        if msg.type == WSMsgType.TEXT: 
            print(f"Received: {msg.data}") 
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
