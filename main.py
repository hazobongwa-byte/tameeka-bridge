import json
import os
import asyncio
import traceback
import logging
from aiohttp import web, WSMsgType
from google.cloud import speech_v1
from google.api_core.exceptions import PermissionDenied

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = None
project_info = {}

if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
    try:
        credentials_json = os.environ['GOOGLE_CREDENTIALS_JSON']
        credentials_info = json.loads(credentials_json)
        project_info = {
            'project_id': credentials_info.get('project_id'),
            'client_email': credentials_info.get('client_email')
        }
        
        client = speech_v1.SpeechClient.from_service_account_info(credentials_info)
        print("Google Speech-to-Text client initialized successfully")
        
    except Exception as e:
        print(f"Failed to initialize Google Cloud: {e}")
        client = None
else:
    print("GOOGLE_CREDENTIALS_JSON not set!")

async def health_check(request):
    return web.json_response({
        "status": "online",
        "bridge": "tameeka-isizulu",
        "google_cloud": {
            "configured": client is not None,
            "project": project_info.get('project_id'),
            "service_account": project_info.get('client_email'),
            "role": "Cloud Speech Client"
        }
    })

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                print(f"Received audio: {len(msg.data)} bytes")
                
                if not client:
                    await ws.send_str("ERROR: Google Cloud not configured")
                    continue
                
                try:
                    config = speech_v1.RecognitionConfig(
                        encoding=speech_v1.RecognitionConfig.AudioEncoding.MULAW,
                        sample_rate_hertz=8000,
                        language_code="zu-ZA",
                        model="phone_call",
                        enable_automatic_punctuation=True
                    )
                    
                    audio = speech_v1.RecognitionAudio(content=msg.data)
                    
                    print("Calling Google Cloud Speech-to-Text API...")
                    response = client.recognize(config=config, audio=audio)
                    
                    print("API Response received")
                    
                    for result in response.results:
                        transcript = result.alternatives[0].transcript.strip()
                        if transcript:
                            print(f"Transcription: {transcript}")
                            await ws.send_str(transcript)
                            break
                    else:
                        await ws.send_str("(listening...)")
                
                except PermissionDenied as e:
                    print("Permission denied error")
                    await ws.send_str("ERROR: Service account lacks permissions.")
                
                except Exception as e:
                    print(f"API Error: {type(e).__name__}: {e}")
                    await ws.send_str(f"ERROR: {type(e).__name__}")
            
            elif msg.type == WSMsgType.TEXT:
                print(f"Text from Vapi: {msg.data}")
            
            elif msg.type == WSMsgType.CLOSE:
                print("WebSocket closing")
                break
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_get('/health', health_check)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    web.run_app(app, port=port, access_log=None)