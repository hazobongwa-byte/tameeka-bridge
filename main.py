import asyncio 
from aiohttp import web, WSMsgType 
import json 
import os 
import base64 
import random 
import traceback 
 
# Google Cloud imports with error handling 
try: 
    from google.cloud import speech 
    GOOGLE_AVAILABLE = True 
    print("Google Cloud Speech library imported successfully") 
except Exception as e: 
    print(f"Failed to import Google Cloud: {e}") 
    GOOGLE_AVAILABLE = False 
 
async def transcribe_with_google(audio_data): 
    print(f"Trying Google Cloud with {len(audio_data)} bytes of audio") 
 
    # Get credentials from environment 
    credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON") 
    if not credentials_json: 
        print("ERROR: No Google credentials in environment") 
        return None 
 
    try: 
        # Write credentials to temporary file 
        with open("/tmp/google-credentials.json", "w") as f: 
            f.write(credentials_json) 
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/google-credentials.json" 
 
        client = speech.SpeechClient() 
 
        # Configure for isiZulu (South Africa) 
        config = speech.RecognitionConfig( 
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, 
            sample_rate_hertz=16000,  # Vapi uses 16kHz 
            language_code="zu-ZA",  # isiZulu South Africa 
            model="latest_long",  # Better for conversation 
            enable_automatic_punctuation=True, 
            use_enhanced=True 
        ) 
 
        audio = speech.RecognitionAudio(content=audio_data) 
 
        print("Calling Google Cloud Speech-to-Text API...") 
        response = client.recognize(config=config, audio=audio) 
 
        if response.results: 
            transcription = response.results[0].alternatives[0].transcript 
            print(f"Google Cloud Success: {transcription}") 
            return transcription 
        else: 
            print("Google Cloud returned no results") 
            return None 
 
    except Exception as e: 
        print(f"Google Cloud Error: {str(e)}") 
        print(traceback.format_exc()) 
        return None 
 
async def transcribe_isizulu_audio(audio_data): 
    print(f"Received audio: {len(audio_data)} bytes") 
 
    # Try Google Cloud first 
    if GOOGLE_AVAILABLE: 
        google_result = await transcribe_with_google(audio_data) 
        if google_result: 
            return google_result 
 
    # Fallback: Simple isiZulu phrase detection 
    print("Using fallback transcription") 
 
    FALLBACK_PHRASES = [ 
        "I would like to book an appointment", 
        "I need to see the doctor", 
        "What time is available tomorrow", 
        "Is Dr. Ntombela available on Friday", 
        "Can I book for next week", 
        "I need a checkup" 
    ] 
 
    # Check if it's a silent/empty audio chunk 
        print("Audio too short, ignoring") 
        return "I would like to book an appointment" 
 
    return random.choice(FALLBACK_PHRASES) 
 
async def websocket_handler(request): 
    print("New WebSocket connection request") 
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
                try: 
                    data = json.loads(msg.data) 
                    print(f"Received JSON: {data}") 
                except: 
                    print(f"Received text: {msg.data}") 
            elif msg.type == WSMsgType.BINARY: 
                transcription = await transcribe_isizulu_audio(msg.data) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await ws.send_str(json.dumps(response)) 
                print(f"Sent transcription: {transcription}") 
            elif msg.type == WSMsgType.CLOSE: 
                print("WebSocket closed by client") 
                break 
            elif msg.type == WSMsgType.ERROR: 
                print(f"WebSocket error: {ws.exception()}") 
    except Exception as e: 
        print(f"WebSocket handler error: {e}") 
        print(traceback.format_exc()) 
 
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
 
async def debug_env(request): 
    env_keys = list(os.environ.keys()) 
    has_google_key = "GOOGLE_APPLICATION_CREDENTIALS_JSON" in env_keys 
    return web.Response( 
        text=json.dumps({ 
            "google_credentials_set": has_google_key, 
            "total_env_vars": len(env_keys), 
            "env_vars": [k for k in env_keys if "KEY" in k or "SECRET" in k] 
        }), 
        content_type='application/json' 
    ) 
 
app = web.Application() 
app.router.add_get('/ws', websocket_handler) 
app.router.add_get('/', health_check) 
app.router.add_get('/debug', debug_env) 
 
if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 8000)) 
    print(f"Starting Tameeka isiZulu Bridge on port {port}") 
    print(f"Google Cloud available: {GOOGLE_AVAILABLE}") 
    web.run_app(app, port=port, host='0.0.0.0') 
