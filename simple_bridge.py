import asyncio 
import websockets 
import json 
import logging 
 
logging.basicConfig(level=logging.INFO) 
 
async def handle_connection(websocket, path): 
    logging.info("Vapi connected!") 
 
    # Vapi sends initial configuration 
    try: 
        init_message = await websocket.recv() 
        logging.info(f"Initial message: {init_message}") 
 
        # Respond with acknowledgement 
        response = { 
            "type": "session", 
            "session": { 
                "id": "test_session_123", 
                "language": "zul" 
            } 
        } 
        await websocket.send(json.dumps(response)) 
 
        # Keep connection alive and handle messages 
        async for message in websocket: 
            if isinstance(message, bytes): 
                # Audio data - send fake transcription for testing 
                transcription = { 
                    "type": "transcription", 
                    "transcription": "I would like to book an appointment", 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await websocket.send(json.dumps(transcription)) 
                logging.info("Sent test transcription") 
 
    except Exception as e: 
        logging.error(f"Error: {e}") 
 
async def health_check(request): 
    from aiohttp import web 
    return web.Response( 
        text=json.dumps({ 
            "status": "online", 
            "service": "Test Bridge", 
            "language": "isiZulu (zul)", 
            "active_connections": 0 
        }), 
        content_type='application/json' 
    ) 
 
async def main(): 
    from aiohttp import web 
 
    # Start WebSocket server 
    ws_server = await websockets.serve(handle_connection, "0.0.0.0", 8765) 
    logging.info(f"WebSocket server running on ws://0.0.0.0:8765") 
 
    # Start HTTP server for health checks 
    app = web.Application() 
    app.router.add_get('/', health_check) 
    runner = web.AppRunner(app) 
    await runner.setup() 
    site = web.TCPSite(runner, "0.0.0.0", 8000) 
    await site.start() 
    logging.info(f"HTTP server running on http://0.0.0.0:8000") 
 
    # Keep running 
    await asyncio.Future() 
 
if __name__ == "__main__": 
    asyncio.run(main()) 
