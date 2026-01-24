import json
from aiohttp import web, WSMsgType

async def health_check(request):
    return web.json_response({"status": "online", "route": "/ws"})

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("=== VAPI CONNECTED ===")
    
    sent = False
    
    async for msg in ws:
        if msg.type == WSMsgType.BINARY and not sent:
            print("Received audio from Vapi")
            
            response = {
                "type": "transcription",
                "transcription": {
                    "text": "book a new appointment",
                    "confidence": 0.95,
                    "isFinal": True
                }
            }
            
            print("SENDING: book a new appointment")
            await ws.send_str(json.dumps(response))
            sent = True
            print("TRANSCRIPTION SENT - CONVERSATION SHOULD CONTINUE")
    
    print("=== VAPI DISCONNECTED ===")
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)  # <- FIXED TO /ws
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    web.run_app(app, port=8080)
