from flask import Flask, request, jsonify
from google.cloud import speech_v1
import os
import json

app = Flask(__name__)

google_client = None

if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
    try:
        credentials_json = os.environ['GOOGLE_CREDENTIALS_JSON']
        credentials_info = json.loads(credentials_json)
        google_client = speech_v1.SpeechClient.from_service_account_info(credentials_info)
        print("Google Speech-to-Text client initialized")
    except Exception as e:
        print(f"Google Cloud init error: {e}")

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready"})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    body_data = request.form.get('body', '')
    speech_result = ''
    
    if 'SpeechResult=' in body_data:
        speech_result = body_data.split('SpeechResult=')[1]
        if '&' in speech_result:
            speech_result = speech_result.split('&')[0]
    
    speech_result = speech_result.lower().strip()
    
    if speech_result:
        if any(word in speech_result for word in ['book', 'new', 'bhuka', 'ngifuna ukubhuka', 'appointment', 'booking', 'make appointment']):
            return jsonify({'action': 'book_appointment'})
        elif any(word in speech_result for word in ['reschedule', 'change', 'hlela', 'shintsha', 'kabusha', 'move appointment']):
            return jsonify({'action': 'reschedule'})
        elif any(word in speech_result for word in ['question', 'ask', 'umbuzo', 'nginombuzo', 'inquiry']):
            return jsonify({'action': 'question'})
    
    if google_client:
        try:
            audio_data = request.form.get('RecordingUrl', '')
            
            if audio_data:
                config = speech_v1.RecognitionConfig(
                    encoding=speech_v1.RecognitionConfig.AudioEncoding.MULAW,
                    sample_rate_hertz=8000,
                    language_code="zu-ZA",
                    model="phone_call",
                    enable_automatic_punctuation=True
                )
                
                audio = speech_v1.RecognitionAudio(content=audio_data)
                response = google_client.recognize(config=config, audio=audio)
                
                for result in response.results:
                    transcript = result.alternatives[0].transcript.strip().lower()
                    if any(word in transcript for word in ['bhuka', 'ngifuna ukubhuka']):
                        return jsonify({'action': 'book_appointment'})
                    elif any(word in transcript for word in ['hlela', 'shintsha', 'kabusha']):
                        return jsonify({'action': 'reschedule'})
                    elif any(word in transcript for word in ['umbuzo', 'nginombuzo']):
                        return jsonify({'action': 'question'})
        except Exception as e:
            print(f"Google Cloud error: {e}")
    
    return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)