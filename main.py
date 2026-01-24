import json
import asyncio
from aiohttp import web, WSMsgType

async def health_check(request):
    return web.json_response({
        "status": "online",
        "service": "tameeka-bridge",
        "endpoint": "/ws"
    })

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("=== VAPI CONNECTION ESTABLISHED ===")
    
    try:
        # Send initial status (REQUIRED by Vapi)
        await ws.send_str(json.dumps({
            "type": "status",
            "status": "connected",
            "message": "Bridge ready"
        }))
        print("Sent 'connected' status to Vapi")
        
        sent = False
        message_count = 0
        
        async for msg in ws:
            message_count += 1
            
            if msg.type == WSMsgType.BINARY:
                print(f"Message #{message_count}: Received {len(msg.data)} bytes of audio")
                
                if not sent:
                    # Send transcription to Vapi
                    transcription = {
                        "type": "transcription",
                        "transcription": {
                            "text": "book a new appointment",
                            "confidence": 0.95,
                            "isFinal": True
                        }
                    }
                    
                    print(f"SENDING TRANSCRIPTION: {json.dumps(transcription)}")
                    await ws.send_str(json.dumps(transcription))
                    print(" Transcription sent to Vapi")
                    sent = True
                    
            elif msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                print(f"TEXT FROM VAPI: {data}")
                
                # Handle Vapi messages
                if data.get("type") == "conversation-update":
                    print(f"Conversation state: {data.get('status')}")
                    
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
                
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("=== VAPI CONNECTION CLOSED ===")
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    port = 8080
    print(f"Tameeka Bridge Server starting on port {port}")
    print("WebSocket endpoint: /ws")
    print("Health check: /health")
    web.run_app(app, port=port, access_log=None)
