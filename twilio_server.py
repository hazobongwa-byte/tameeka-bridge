from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready - TEST ENDPOINTS: /test-get?speech=book or /test-post"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    print(f"TEST GET: '{speech}'")
    
    book_words = [
        'book', 'books', 'booking', 'booked', 'appointment', 'appointments',
        'bhuka', 'bhukha', 'bhukka', 'bukha', 'booka', 'buka',
        'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela',
        'make appointment', 'new appointment', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 're schedule', 'rice schedule', 'ricehedul',
        'change', 'changes', 'changing', 'move', 'moving',
        'hlela', 'hlelah', 'shintsha', 'shintshah', 'guqula',
        'change appointment', 'move appointment', 'postpone'
    ]
    
    question_words = [
        'question', 'questions', 'questio', 'questiom',
        'ask', 'asking', 'inquiry', 'help',
        'umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo',
        'have question', 'got question', 'need help'
    ]
    
    if any(word in speech for word in book_words):
        return jsonify({'action': 'book_appointment', 'method': 'GET', 'heard': speech})
    elif any(word in speech for word in reschedule_words):
        return jsonify({'action': 'reschedule', 'method': 'GET', 'heard': speech})
    elif any(word in speech for word in question_words):
        return jsonify({'action': 'question', 'method': 'GET', 'heard': speech})
    else:
        return jsonify({'action': 'unknown', 'method': 'GET', 'heard': speech})

@app.route('/test-post', methods=['POST'])
def test_post():
    speech = request.form.get('speech', '').lower().strip()
    print(f"TEST POST: '{speech}'")
    
    book_words = [
        'book', 'books', 'booking', 'booked', 'appointment', 'appointments',
        'bhuka', 'bhukha', 'bhukka', 'bukha', 'booka', 'buka',
        'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela',
        'make appointment', 'new appointment', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 're schedule', 'rice schedule', 'ricehedul',
        'change', 'changes', 'changing', 'move', 'moving',
        'hlela', 'hlelah', 'shintsha', 'shintshah', 'guqula',
        'change appointment', 'move appointment', 'postpone'
    ]
    
    question_words = [
        'question', 'questions', 'questio', 'questiom',
        'ask', 'asking', 'inquiry', 'help',
        'umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo',
        'have question', 'got question', 'need help'
    ]
    
    if any(word in speech for word in book_words):
        return jsonify({'action': 'book_appointment', 'method': 'POST', 'heard': speech})
    elif any(word in speech for word in reschedule_words):
        return jsonify({'action': 'reschedule', 'method': 'POST', 'heard': speech})
    elif any(word in speech for word in question_words):
        return jsonify({'action': 'question', 'method': 'POST', 'heard': speech})
    else:
        return jsonify({'action': 'unknown', 'method': 'POST', 'heard': speech})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    body_data = request.form.get('body', '')
    print(f"TWILIO: Raw body data: '{body_data}'")
    
    speech_result = ''
    
    if 'SpeechResult=' in body_data:
        speech_result = body_data.split('SpeechResult=')[1]
        if '&' in speech_result:
            speech_result = speech_result.split('&')[0]
    
    speech_result = speech_result.lower().strip()
    print(f"TWILIO: Extracted speech: '{speech_result}'")
    
    if not speech_result:
        print("TWILIO: Speech is EMPTY")
        return jsonify({'action': 'unknown'})
    
    book_words = [
        'book', 'books', 'booking', 'booked', 'appointment', 'appointments',
        'bhuka', 'bhukha', 'bhukka', 'bukha', 'booka', 'buka',
        'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela',
        'make appointment', 'new appointment', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 're schedule', 'rice schedule', 'ricehedul',
        'change', 'changes', 'changing', 'move', 'moving',
        'hlela', 'hlelah', 'shintsha', 'shintshah', 'guqula',
        'change appointment', 'move appointment', 'postpone'
    ]
    
    question_words = [
        'question', 'questions', 'questio', 'questiom',
        'ask', 'asking', 'inquiry', 'help',
        'umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo',
        'have question', 'got question', 'need help'
    ]
    
    if any(word in speech_result for word in book_words):
        print("TWILIO: Matched BOOK_APPOINTMENT")
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in reschedule_words):
        print("TWILIO: Matched RESCHEDULE")
        return jsonify({'action': 'reschedule'})
    elif any(word in speech_result for word in question_words):
        print("TWILIO: Matched QUESTION")
        return jsonify({'action': 'question'})
    else:
        print("TWILIO: No match")
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)