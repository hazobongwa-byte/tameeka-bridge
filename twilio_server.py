from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Fast assistant with improved reschedule"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    
    book_words = [
        'book', 'books', 'booking', 'booked', 'appointment',
        'bhuka', 'bhukha', 'bhukka', 'bukha', 'booka', 'buka',
        'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela',
        'make appointment', 'new appointment', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 're schedule', 'rice schedule', 'ricehedul',
        'rice hedge', 'rice hedger', 're shed you', 're shedger',
        'change', 'changing', 'changed', 'move', 'moving', 'moved',
        'hlela', 'hlelah', 'shintsha', 'shintshah', 'guqula',
        'change appointment', 'move appointment', 'postpone',
        'reschedule appointment', 'change my appointment'
    ]
    
    question_words = [
        'question', 'questions', 'ask', 'asking', 'inquiry', 'help',
        'umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo', 'ndaba',
        'have question', 'got question', 'need help'
    ]
    
    if any(word in speech for word in book_words):
        return jsonify({'action': 'book_appointment', 'heard': speech})
    elif any(word in speech for word in reschedule_words):
        return jsonify({'action': 'reschedule', 'heard': speech})
    elif any(word in speech for word in question_words):
        return jsonify({'action': 'question', 'heard': speech})
    else:
        return jsonify({'action': 'unknown', 'heard': speech})

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
    
    book_words = [
        'book', 'books', 'booking', 'booked', 'appointment',
        'bhuka', 'bhukha', 'bhukka', 'bukha', 'booka', 'buka',
        'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela',
        'make appointment', 'new appointment', 'schedule'
    ]
    
    reschedule_words = [
        'reschedule', 're schedule', 'rice schedule', 'ricehedul',
        'rice hedge', 'rice hedger', 're shed you', 're shedger',
        'change', 'changing', 'changed', 'move', 'moving', 'moved',
        'hlela', 'hlelah', 'shintsha', 'shintshah', 'guqula',
        'change appointment', 'move appointment', 'postpone',
        'reschedule appointment', 'change my appointment'
    ]
    
    question_words = [
        'question', 'questions', 'ask', 'asking', 'inquiry', 'help',
        'umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo', 'ndaba',
        'have question', 'got question', 'need help'
    ]
    
    if any(word in speech_result for word in book_words):
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in reschedule_words):
        return jsonify({'action': 'reschedule'})
    elif any(word in speech_result for word in question_words):
        return jsonify({'action': 'question'})
    else:
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)