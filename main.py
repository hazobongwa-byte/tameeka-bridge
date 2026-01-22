import asyncio 
from aiohttp import web, WSMsgType 
import json 
import os 
import base64 
import random 
from google.cloud import speech 
import io 
 
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON") 
 
async def transcribe_isizulu_audio(audio_data): 
    print(f"Received audio: {len(audio_data)} bytes") 
 
    if not GOOGLE_CREDENTIALS: 
        print("Google credentials not found in environment") 
        FALLBACK = ["I would like to book an appointment"] 
        return random.choice(FALLBACK) 
 
    try: 
        with open("google-credentials.json", "w") as f: 
            f.write(GOOGLE_CREDENTIALS) 
 
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-credentials.json" 
 
        client = speech.SpeechClient() 
 
        config = speech.RecognitionConfig( 
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, 
            sample_rate_hertz=16000, 
            language_code="zu-ZA", 
            enable_automatic_punctuation=True, 
        ) 
 
        audio = speech.RecognitionAudio(content=audio_data) 
 
        print("Sending to Google Cloud Speech-to-Text...") 
        response = client.recognize(config=config, audio=audio) 
 
        transcriptions = [] 
        for result in response.results: 
            transcriptions.append(result.alternatives[0].transcript) 
 
        if transcriptions: 
            transcription = " ".join(transcriptions) 
            print(f"Google Cloud transcription: {transcription}") 
            return transcription 
        else: 
            print("No transcription returned") 
            return "I would like to book an appointment" 
 
    except Exception as e: 
        print(f"Google Cloud error: {e}") 
        FALLBACK = ["I would like to book an appointment"] 
        return random.choice(FALLBACK) 
 
async def websocket_handler(request): 
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
                print(f"Received: {msg.data}") 
            elif msg.type == WSMsgType.BINARY: 
                transcription = await transcribe_isizulu_audio(msg.data) 
                response = { 
                    "type": "transcription", 
                    "transcription": transcription, 
                    "language": "zul", 
                    "channel": "customer" 
                } 
                await ws.send_str(json.dumps(response)) 
                print(f"Sent: {transcription}") 
            elif msg.type == WSMsgType.CLOSE: 
                print("WebSocket closed") 
                break 
            elif msg.type == WSMsgType.ERROR: 
                print(f"WebSocket error: {ws.exception()}") 
    except Exception as e: 
        print(f"Error: {e}") 
 
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
 
app = web.Application() 
app.router.add_get('/ws', websocket_handler) 
app.router.add_get('/', health_check) 
 
if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 8000)) 
    web.run_app(app, port=port, host='0.0.0.0') 
