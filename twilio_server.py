from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Fast assistant ready"})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    body_data = request.form.get('body', '')
    
    if 'SpeechResult=' not in body_data:
        return jsonify({'action': 'unknown'})
    
    speech_result = body_data.split('SpeechResult=')[1].split('&')[0]
    speech_result = speech_result.lower().strip()
    
    if not speech_result:
        return jsonify({'action': 'unknown'})
    
    book_words = ['book', 'bhuka', 'appointment', 'schedule', 'ngifuna', 'ngicela']
    reschedule_words = ['reschedule', 'change', 'hlela', 'shintsha', 'move']
    question_words = ['question', 'ask', 'umbuzo', 'help', 'buzisa']
    
    for word in book_words:
        if word in speech_result:
            return jsonify({'action': 'book_appointment'})
    
    for word in reschedule_words:
        if word in speech_result:
            return jsonify({'action': 'reschedule'})
    
    for word in question_words:
        if word in speech_result:
            return jsonify({'action': 'question'})
    
    return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)