from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Fixed Zulu booking understanding"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    
    book_phrases = [
        'book', 'booking', 'appointment', 'new appointment', 'make appointment',
        'bhuka', 'ukubhuka', 'ngifuna ukubhuka', 'ngicela ukubhuka',
        'bengisacela ukubhuka', 'bengisacela uku bhuka',
        'bengisacela uku bhuka i-appointment entsha',
        'bengisacela ungibhukise', 'awungibhukise',
        'ngifuna ukubhuka', 'ngicela ukubhuka',
        'being a seller cook book', 'being a seller cook',
        'engineer cook book', 'engineer cook',
        'engineer fun cook', 'engineer fun',
        'cook book', 'cook', 'booker', 'buka', 'booka',
        'bhuk', 'booki', 'appoint'
    ]
    
    change_phrases = [
        'change', 'change appointment', 'move', 'reschedule',
        'shintsha', 'hlela', 'guqula', 'ukushintsha',
        'ngifuna ukushintsha', 'ngicela ukushintsha'
    ]
    
    question_phrases = [
        'question', 'ask', 'inquiry', 'help',
        'umbuzo', 'nginomubuzo', 'ngonombuzo',
        'bengisacela ukubuza', 'ngifuna ukubuza',
        'nginombuzo', 'nginendaba', 'ndaba'
    ]
    
    speech_lower = speech.lower()
    
    for phrase in book_phrases:
        if phrase in speech_lower:
            return jsonify({'action': 'book_appointment', 'heard': speech})
    
    for phrase in change_phrases:
        if phrase in speech_lower:
            return jsonify({'action': 'reschedule', 'heard': speech})
    
    for phrase in question_phrases:
        if phrase in speech_lower:
            return jsonify({'action': 'question', 'heard': speech})
    
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
    print(f"DEBUG: Twilio heard: '{speech_result}'")
    
    if not speech_result:
        return jsonify({'action': 'unknown'})
    
    book_phrases = [
        'book', 'booking', 'appointment', 'new appointment', 'make appointment',
        'bhuka', 'ukubhuka', 'ngifuna ukubhuka', 'ngicela ukubhuka',
        'bengisacela ukubhuka', 'bengisacela uku bhuka',
        'bengisacela uku bhuka i-appointment entsha',
        'bengisacela ungibhukise', 'awungibhukise',
        'ngifuna ukubhuka', 'ngicela ukubhuka',
        'being a seller cook book', 'being a seller cook',
        'engineer cook book', 'engineer cook',
        'engineer fun cook', 'engineer fun',
        'cook book', 'cook', 'booker', 'buka', 'booka',
        'bhuk', 'booki', 'appoint'
    ]
    
    change_phrases = [
        'change', 'change appointment', 'move', 'reschedule',
        'shintsha', 'hlela', 'guqula', 'ukushintsha',
        'ngifuna ukushintsha', 'ngicela ukushintsha'
    ]
    
    question_phrases = [
        'question', 'ask', 'inquiry', 'help',
        'umbuzo', 'nginomubuzo', 'ngonombuzo',
        'bengisacela ukubuza', 'ngifuna ukubuza',
        'nginombuzo', 'nginendaba', 'ndaba'
    ]
    
    for phrase in book_phrases:
        if phrase in speech_result:
            print(f"DEBUG: Matched book phrase: '{phrase}'")
            return jsonify({'action': 'book_appointment'})
    
    for phrase in change_phrases:
        if phrase in speech_result:
            print(f"DEBUG: Matched change phrase: '{phrase}'")
            return jsonify({'action': 'reschedule'})
    
    for phrase in question_phrases:
        if phrase in speech_result:
            print(f"DEBUG: Matched question phrase: '{phrase}'")
            return jsonify({'action': 'question'})
    
    print("DEBUG: No match found")
    return jsonify({'action': 'unknown'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)