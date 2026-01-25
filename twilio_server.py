from flask import Flask, request, jsonify

app = Flask(__name__)

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
    
    if not speech_result:
        return jsonify({'action': 'unknown'})
    
    if any(word in speech_result for word in ['book', 'new', 'bhuka', 'ngifuna', 'ukubhuka', 'appointment', 'booking']):
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in ['reschedule', 'change', 'hlela', 'shintsha', 'kabusha', 'move']):
        return jsonify({'action': 'reschedule'})
    elif any(word in speech_result for word in ['question', 'ask', 'umbuzo', 'nginombuzo', 'inquiry']):
        return jsonify({'action': 'question'})
    else:
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)