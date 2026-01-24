import json
import os
import asyncio
from aiohttp import web, WSMsgType
from datetime import datetime, timezone

async def health_check(request):
    return web.json_response({
        "status": "online",
        "service": "tameeka-bridge",
        "mode": "fixed-response-single",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    transcription_sent = False
    
    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
    print(f"\n[{current_time}] New Vapi connection")
    
    try:
        await ws.send_str(json.dumps({
            "type": "status",
            "status": "connected",
            "message": "Bridge ready"
        }))
        
        async for msg in ws:
            current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            
            if msg.type == WSMsgType.BINARY and not transcription_sent:
                print(f"[{current_time}] Received {len(msg.data)} bytes of audio")
                
                transcription = {
                    "type": "transcription",
                    "transcription": {
                        "text": "book a new appointment",
                        "confidence": 0.95,
                        "isFinal": True
                    }
                }
                
                print(f"[{current_time}] Sending: 'book a new appointment'")
                await ws.send_str(json.dumps(transcription))
                print(f"[{current_time}] Transcription sent successfully!")
                transcription_sent = True
                
            elif msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"[{current_time}] Text message: {data.get('type', 'unknown')}")
                
    except Exception as e:
        current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
        print(f"[{current_time}] Error: {e}")
    
    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
    print(f"[{current_time}] Connection closed")
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting single-response bridge on port {port}")
    web.run_app(app, port=port, access_log=None)