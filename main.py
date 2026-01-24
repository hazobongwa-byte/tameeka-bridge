import json
from aiohttp import web, WSMsgType

async def health_check(request):
    return web.json_response({"status": "online"})

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    print("NEW CALL")
    
    sent = False
    
    async for msg in ws:
        if msg.type == WSMsgType.BINARY and not sent:
            print("Audio received")
            
            response = {
                "type": "transcription",
                "transcription": {
                    "text": "book a new appointment",
                    "confidence": 0.95,
                    "isFinal": True
                }
            }
            
            print("Sending transcription")
            await ws.send_str(json.dumps(response))
            sent = True
    
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    web.run_app(app, port=8080)
