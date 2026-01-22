from aiohttp import web, WSMsgType 
import json 
import os 
 
async def websocket_handler(request): 
    ws = web.WebSocketResponse() 
    await ws.prepare(request) 
 
    print("? Vapi connected!") 
 
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
            response = { 
                "type": "transcription", 
                "transcription": "I would like to book an appointment", 
                "language": "zul", 
                "channel": "customer" 
            } 
            await ws.send_str(json.dumps(response)) 
            print("? Sent test transcription") 
        elif msg.type == WSMsgType.ERROR: 
            print(f"WebSocket error: {ws.exception()}") 
 
    print("? Vapi disconnected") 
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
