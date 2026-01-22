from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import requests
import io
import uvicorn

VULAVULA_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGUzNWIwNGItMTUyYi00MjIwLWI2NzEtMjE3YWUwY2ZlNjc5Iiwia2V5Y2hhaW5faWQiOiIwOWUxZGJlYi0zNWJlLTQ0ZTEtYWFiMS05YzcwYmZiYWRjMmMiLCJwcm9qZWN0X2lkIjoiZmRjZWY1OGItYzA3MC00NTBjLWExNTgtN2Y2OWM2YzcyNTM3IiwiY3JlYXRlZF9hdCI6IjIwMjYtMDEtMjFUMTQ6NDY6MTIuMDQ5MTY4In0.E4EhHdAAieWD2UW25z1F5Yp0sOLaCLHTN8Qv9V-SV44"
VULAVULA_SYNC_URL = "https://api.lelapa.ai/v1/transcribe/sync"

app = FastAPI()
active_connections = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    print(f"Vapi connected. Active connections: {len(active_connections)}")

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            print(f"Received {len(audio_bytes)} bytes of audio")

            transcript = ""
            
            try:
                audio_file = io.BytesIO(audio_bytes)
                
                files = {'file': ('audio_chunk.wav', audio_file, 'audio/wav')}
                params = {'lang_code': 'zul'}
                headers = {'Authorization': f'Bearer {eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGUzNWIwNGItMTUyYi00MjIwLWI2NzEtMjE3YWUwY2ZlNjc5Iiwia2V5Y2hhaW5faWQiOiIwOWUxZGJlYi0zNWJlLTQ0ZTEtYWFiMS05YzcwYmZiYWRjMmMiLCJwcm9qZWN0X2lkIjoiZmRjZWY1OGItYzA3MC00NTBjLWExNTgtN2Y2OWM2YzcyNTM3IiwiY3JlYXRlZF9hdCI6IjIwMjYtMDEtMjFUMTQ6NDY6MTIuMDQ5MTY4In0.E4EhHdAAieWD2UW25z1F5Yp0sOLaCLHTN8Qv9V-SV44}'}
                
                print("Sending to Vulavula API...")
                api_response = requests.post(
                    VULAVULA_SYNC_URL,
                    files=files,
                    params=params,
                    headers=headers,
                    timeout=15
                )
                
                if api_response.status_code == 200:
                    result = api_response.json()
                    transcript = result.get('transcription_text', '')
                    print(f"Vulavula Response: {transcript}")
                else:
                    print(f"Vulavula Error {api_response.status_code}: {api_response.text[:100]}")
                    transcript = f"[Error: {api_response.status_code}]"
                    
            except requests.exceptions.Timeout:
                print("Vulavula API timeout (15s)")
                transcript = "[Timeout]"
            except Exception as e:
                print(f"Error calling Vulavula: {e}")
                transcript = "[Processing Error]"
            
            response = {"text": transcript}
            await websocket.send_json(response)
            print(f"Sent to Vapi: {transcript[:50]}...")
            
    except WebSocketDisconnect:
        print(f"Vapi disconnected. Active connections: {len(active_connections)-1}")
        if connection_id in active_connections:
            del active_connections[connection_id]
    except Exception as e:
        print(f"Critical WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

@app.get("/")
async def health_check():
    return {
        "status": "online",
        "service": "Vapi-Vulavula Bridge",
        "language": "isiZulu (zul)",
        "active_connections": len(active_connections)
    }

@app.get("/test")
async def test_page():
    html_content = """
    <html><body style='font-family: Arial; padding: 20px;'>
        <h2>✅ Bridge Server is Running</h2>
        <p><strong>Service:</strong> Vapi to Vulavula (isiZulu)</p>
        <p><strong>WebSocket URL for Vapi:</strong> <code>ws://localhost:8000/ws</code></p>
        <p><strong>Health Check:</strong> <a href='/'>/</a></p>
        <hr>
        <p>Next: Configure Vapi's "Custom Speech-to-Text" to use the URL above.</p>
    </body></html>
    """
    return HTMLResponse(html_content)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 VAPI-VULAVULA BRIDGE SERVER")
    print("="*50)
    print("📍 Local Health Check: http://localhost:8000")
    print("📍 Test Page: http://localhost:8000/test")
    print("🔌 WebSocket for Vapi: ws://localhost:8000/ws")
    print("="*50)
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)