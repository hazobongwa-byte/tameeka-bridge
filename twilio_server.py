from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready"})

@app.route('/twilio-webhook', methods=['POST', 'GET'])
def twilio_webhook():
    if request.method == 'GET':
        speech = request.args.get('SpeechResult', '')
        speech_result = speech.lower()
    else:
        speech_result = request.form.get('SpeechResult', '').lower()
    
    print(f"TWILIO WEBHOOK: Received speech: '{speech_result}'")
    
    if any(word in speech_result for word in ['book', 'new', 'bhuka', 'ngifuna ukubhuka']):
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in ['reschedule', 'change', 'hlela', 'shintsha', 'kabusha']):
        return jsonify({'action': 'reschedule'})
    elif any(word in speech_result for word in ['question', 'ask', 'umbuzo', 'nginombuzo']):
        return jsonify({'action': 'question'})
    else:
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)