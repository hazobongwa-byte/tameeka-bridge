import asyncio 
from aiohttp import web, WSMsgType, ClientSession 
import json 
import os 
import base64 
 
VULAVULA_API_URL = "https://api.lelapa.ai/v1/speech-to-text" 
 
async def transcribe_isizulu_audio(audio_data): 
    api_key = os.environ.get("VULAVULA_API_KEY") 
    if not api_key: 
        print("ERROR: Vulavula API key not set in environment") 
        return "I would like to book an appointment" 
 
    print("Sending audio to Vulavula API...") 
    async with ClientSession() as session: 
        headers = { 
            "Authorization": f"Bearer {api_key}", 
            "Content-Type": "application/json" 
        } 
 
        audio_base64 = base64.b64encode(audio_data).decode('utf-8') 
 
        payload = { 
            "audio": audio_base64, 
            "language": "zul", 
            "transcription_format": "text" 
        } 
 
        try: 
            print(f"Sending to: {VULAVULA_API_URL}") 
            async with session.post(VULAVULA_API_URL, json=payload, headers=headers) as response: 
                response_text = await response.text() 
                print(f"API Response status: {response.status}") 
                print(f"API Response body: {response_text[:200]}") 
 
                if response.status == 200: 
                    try: 
                        result = json.loads(response_text) 
                        transcription = result.get("transcription", result.get("text", "")).strip() 
                        if transcription: 
                            print(f"Vulavula API transcription: {transcription}") 
                            return transcription 
                        else: 
                            print("Vulavula API returned empty transcription") 
                            return "I would like to book an appointment" 
                    except json.JSONDecodeError: 
                        print(f"Failed to parse JSON: {response_text}") 
                        return "I would like to book an appointment" 
                else: 
                    print(f"Vulavula API error: {response.status} - {response_text}") 
                    return "I would like to book an appointment" 
        except Exception as e: 
            print(f"Vulavula API exception: {e}") 
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
 
    transcription_sent = False 
 
    async for msg in ws: 
        if msg.type == WSMsgType.TEXT: 
            print(f"Received text: {msg.data}") 
        elif msg.type == WSMsgType.BINARY: 
            if not transcription_sent: 
                transcription = await transcribe_isizulu_audio(msg.data) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await ws.send_str(json.dumps(response)) 
                print(f"Sent transcription: {transcription}") 
                transcription_sent = True 
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
