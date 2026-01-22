from aiohttp import web, WSMsgType 
import json 
import os 
import random 
 
FALLBACK_PHRASES = [ 
    "I would like to book an appointment", 
    "I need to see the doctor", 
    "What time is available tomorrow", 
    "Is Dr. Ntombela available on Friday" 
] 
 
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
                print(f"Received: {msg.data}") 
            elif msg.type == WSMsgType.BINARY: 
                transcription = random.choice(FALLBACK_PHRASES) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await ws.send_str(json.dumps(response)) 
                print(f"Sent: {transcription}") 
            elif msg.type == WSMsgType.CLOSE: 
                print("WebSocket closed") 
                break 
    except Exception as e: 
        print(f"Error: {e}") 
 
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
    print(f"Starting server on port {port}") 
    web.run_app(app, port=port, host='0.0.0.0') 
