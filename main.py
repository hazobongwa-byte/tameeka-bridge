import json
import os
from aiohttp import web, WSMsgType

async def health_check(request):
    return web.json_response({
        "status": "online",
        "service": "tameeka-bridge",
        "mode": "simple-fixed-response"
    })

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("=== NEW CALL STARTED ===")
    
    sent = False
    
    try:
        await ws.send_str(json.dumps({
            "type": "status",
            "status": "connected"
        }))
        
        async for msg in ws:
            if msg.type == WSMsgType.BINARY and not sent:
                print(f"Audio received: {len(msg.data)} bytes")
                
                transcription = {
                    "type": "transcription",
                    "transcription": {
                        "text": "book a new appointment",
                        "confidence": 0.95,
                        "isFinal": True
                    }
                }
                
                print("SENDING: 'book a new appointment'")
                await ws.send_str(json.dumps(transcription))
                print("TRANSCRIPTION SENT - ONLY ONCE")
                sent = True
                
    except Exception as e:
        print(f"Error: {e}")
    
    print("=== CALL ENDED ===")
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Bridge server starting on port {port}")
    web.run_app(app, port=port)