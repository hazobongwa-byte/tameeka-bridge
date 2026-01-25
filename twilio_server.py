from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Bilingual English/isiZulu assistant ready"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    
    zulu_book = ['bhuka', 'bhukha', 'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela']
    zulu_reschedule = ['hlela', 'shintsha', 'guqula', 'kabusha']
    zulu_question = ['umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo', 'ndaba']
    
    english_book = ['book', 'booking', 'appointment', 'schedule', 'make appointment']
    english_reschedule = ['reschedule', 'change', 'move', 'postpone']
    english_question = ['question', 'ask', 'inquiry', 'help']
    
    is_zulu = any(word in speech for word in zulu_book + zulu_reschedule + zulu_question)
    
    if any(word in speech for word in zulu_book + english_book):
        return jsonify({
            'action': 'book_appointment', 
            'language': 'zulu' if is_zulu else 'english',
            'heard': speech
        })
    elif any(word in speech for word in zulu_reschedule + english_reschedule):
        return jsonify({
            'action': 'reschedule', 
            'language': 'zulu' if is_zulu else 'english',
            'heard': speech
        })
    elif any(word in speech for word in zulu_question + english_question):
        return jsonify({
            'action': 'question', 
            'language': 'zulu' if is_zulu else 'english',
            'heard': speech
        })
    else:
        return jsonify({
            'action': 'unknown', 
            'language': 'english',
            'heard': speech
        })

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
        return jsonify({'action': 'unknown', 'language': 'english'})
    
    zulu_book = ['bhuka', 'bhukha', 'ukubhuka', 'ngifuna', 'ngicela', 'funa', 'cela']
    zulu_reschedule = ['hlela', 'shintsha', 'guqula', 'kabusha']
    zulu_question = ['umbuzo', 'umbuza', 'nginombuzo', 'buzisa', 'buzo', 'ndaba']
    
    english_book = ['book', 'booking', 'appointment', 'schedule', 'make appointment']
    english_reschedule = ['reschedule', 'change', 'move', 'postpone']
    english_question = ['question', 'ask', 'inquiry', 'help']
    
    is_zulu = any(word in speech_result for word in zulu_book + zulu_reschedule + zulu_question)
    
    if any(word in speech_result for word in zulu_book + english_book):
        return jsonify({
            'action': 'book_appointment',
            'language': 'zulu' if is_zulu else 'english'
        })
    elif any(word in speech_result for word in zulu_reschedule + english_reschedule):
        return jsonify({
            'action': 'reschedule',
            'language': 'zulu' if is_zulu else 'english'
        })
    elif any(word in speech_result for word in zulu_question + english_question):
        return jsonify({
            'action': 'question',
            'language': 'zulu' if is_zulu else 'english'
        })
    else:
        return jsonify({'action': 'unknown', 'language': 'english'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)