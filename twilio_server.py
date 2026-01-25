from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready"})

@app.route('/twilio-webhook', methods=['POST', 'GET'])
def twilio_webhook():
    print("=== NEW REQUEST ===")
    print(f"Method: {request.method}")
    print(f"Form data: {dict(request.form)}")
    print(f"Args data: {dict(request.args)}")
    
    if request.method == 'GET':
        speech = request.args.get('SpeechResult', '')
        speech_result = speech.lower()
    else:
        body_data = request.form.get('body', '')
        print(f"Raw body data: '{body_data}'")
        
        speech_result = ''
        if 'SpeechResult=' in body_data:
            speech_result = body_data.split('SpeechResult=')[1]
            if '&' in speech_result:
                speech_result = speech_result.split('&')[0]
        
        speech_result = speech_result.lower().strip()
    
    print(f"Extracted speech: '{speech_result}'")
    
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