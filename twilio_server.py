from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Assistant understands: book, change appointment, question"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    
    book_words = ['book', 'bhuka', 'appointment']
    change_words = ['change', 'change appointment', 'move', 'shintsha', 'hlela']
    question_words = ['question', 'ask', 'umbuzo']
    
    if any(word in speech for word in book_words):
        return jsonify({'action': 'book_appointment', 'heard': speech})
    elif any(word in speech for word in change_words):
        return jsonify({'action': 'change_appointment', 'heard': speech})
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
    
    book_words = ['book', 'bhuka', 'appointment']
    change_words = ['change', 'change appointment', 'move', 'shintsha', 'hlela']
    question_words = ['question', 'ask', 'umbuzo']
    
    if any(word in speech_result for word in book_words):
        return jsonify({'action': 'book_appointment'})
    elif any(word in speech_result for word in change_words):
        return jsonify({'action': 'change_appointment'})
    elif any(word in speech_result for word in question_words):
        return jsonify({'action': 'question'})
    else:
        return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)