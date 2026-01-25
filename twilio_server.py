from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready"})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    body_data = request.form.get('body', '')
    print(f"DEBUG: Raw body data: '{body_data}'")
    
    speech_result = ''
    
    if 'SpeechResult=' in body_data:
        speech_result = body_data.split('SpeechResult=')[1]
        if '&' in speech_result:
            speech_result = speech_result.split('&')[0]
    
    speech_result = speech_result.lower().strip()
    print(f"DEBUG: Extracted speech: '{speech_result}'")
    
    if not speech_result:
        print("DEBUG: Speech is EMPTY")
        return jsonify({'action': 'unknown'})
    
    book_words = [
        'book', 'new', 'appointment', 'booking', 'make appointment',
        'bhuka', 'ukubhuka', 'ngifuna', 'funa', 'ngicela', 'cela',
        'ngicela ukubhuka', 'ngifuna ukubhuka', 'bhukha', 'ukubhukha',
        'booking', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 'change', 'move', 'postpone',
        'hlela', 'shintsha', 'kabusha', 'hlela kabusha',
        'guqula', 'shintsha isikhathi'
    ]
    
    question_words = [
        'question', 'ask', 'inquiry', 'help',
        'umbuzo', 'nginombuzo', 'buzo', 'buzisa',
        'ndaba', 'nginendaba'
    ]
    
    if any(word in speech_result for word in book_words):
        print("DEBUG: Matched BOOK_APPOINTMENT")
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in reschedule_words):
        print("DEBUG: Matched RESCHEDULE")
        return jsonify({'action': 'reschedule'})
    elif any(word in speech_result for word in question_words):
        print("DEBUG: Matched QUESTION")
        return jsonify({'action': 'question'})
    else:
        print("DEBUG: No match - returning UNKNOWN")
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)