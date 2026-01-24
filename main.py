import json
import os
import asyncio
from aiohttp import web, WSMsgType
from datetime import datetime

async def health_check(request):
    return web.json_response({
        "status": "online",
        "service": "tameeka-bridge",
        "mode": "fixed-response",
        "timestamp": datetime.utcnow().isoformat()
    })

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] New Vapi connection")
    
    try:
        await ws.send_str(json.dumps({
            "type": "status",
            "status": "connected",
            "message": "Bridge ready"
        }))
        
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Received {len(msg.data)} bytes of audio")
                
                transcription = {
                    "type": "transcription",
                    "transcription": {
                        "text": "book a new appointment",
                        "confidence": 0.95,
                        "isFinal": True
                    }
                }
                
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Sending: 'book a new appointment'")
                await ws.send_str(json.dumps(transcription))
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Transcription sent successfully!")
                
            elif msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Text message: {data.get('type', 'unknown')}")
                
    except Exception as e:
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Error: {e}")
    
    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Connection closed")
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting fixed-response bridge on port {port}")
    web.run_app(app, port=port, access_log=None)