from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

conversations = {}

@app.route('/')
def home():
    return jsonify({"message": "Conversation assistant ready"})

@app.route('/test-get', methods=['GET'])
def test_get():
    speech = request.args.get('speech', '').lower().strip()
    
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
        return jsonify({'action': 'book_appointment', 'heard': speech})
    elif any(word in speech for word in reschedule_words):
        return jsonify({'action': 'reschedule', 'heard': speech})
    elif any(word in speech for word in question_words):
        return jsonify({'action': 'question', 'heard': speech})
    else:
        return jsonify({'action': 'unknown', 'heard': speech})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    from_number = request.form.get('From', '')
    call_sid = request.form.get('CallSid', '')
    
    body_data = request.form.get('body', '')
    
    speech_result = ''
    if 'SpeechResult=' in body_data:
        speech_result = body_data.split('SpeechResult=')[1]
        if '&' in speech_result:
            speech_result = speech_result.split('&')[0]
    
    speech_result = speech_result.lower().strip()
    print(f"Call {call_sid[-6:]}: '{speech_result}'")
    
    if call_sid not in conversations:
        conversations[call_sid] = {
            'step': 1,
            'name': '',
            'phone': from_number,
            'appointment_type': '',
            'start_time': datetime.now().strftime("%H:%M:%S")
        }
    
    current = conversations[call_sid]
    step = current['step']
    
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
    
    name_keywords = ['my name', 'name is', 'igama', 'ngingu', 'ngu', 'mina', 'i am']
    
    if step == 1:
        current['step'] = 2
        return jsonify({
            'actions': [
                {
                    'say': {
                        'speech': "Sawubona! Ngingumsiza wakwaDokotela Ntombela. Ungangitshela igama lakho? Hello! I am Dr. Ntombela's assistant. Can you tell me your name?",
                        'language': 'en-US'
                    }
                },
                {
                    'listen': {
                        'speech_timeout': 10
                    }
                }
            ]
        })
    
    elif step == 2:
        if speech_result:
            for word in name_keywords:
                if word in speech_result:
                    words = speech_result.split()
                    for i, w in enumerate(words):
                        if w in ['is', 'ngingu', 'ngu'] and i+1 < len(words):
                            current['name'] = words[i+1]
                            break
                    if not current['name']:
                        current['name'] = speech_result.split()[-1]
                    break
            
            if not current['name']:
                current['name'] = speech_result.split()[0] if speech_result.split() else 'mfowethu'
            
            current['step'] = 3
            name = current['name']
            
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {name}! Ungangitshela ukuthi ufuna ukwenzani? Ungabhuka isikhathi, ushintshe isikhathi, noma unombuzo? Thank you {name}! Can you tell me what you need? Do you want to book, reschedule, or ask a question?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        else:
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': "Angizwanga kahle. Ungangitshela igama lakho futhi? I didn't hear you well. Can you tell me your name again?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
    
    elif step == 3:
        if any(word in speech_result for word in book_words):
            current['appointment_type'] = 'book'
            current['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"{current['name']}, ufuna ukubhuka isikhathi. Ungangitshela usuku ofuna ukuzofika ngalo? NjengoMsombuluko, noma uLwesibili? {current['name']}, you want to book an appointment. Can you tell me what day you want to come? Like Monday or Tuesday?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        
        elif any(word in speech_result for word in reschedule_words):
            current['appointment_type'] = 'reschedule'
            current['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"{current['name']}, ufuna ukushintsha isikhathi. Ungangitshela inombolo yesikhathi sakho noma igama? {current['name']}, you want to reschedule. Can you tell me your appointment number or name?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        
        elif any(word in speech_result for word in question_words):
            current['appointment_type'] = 'question'
            current['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"{current['name']}, unombuzo. Ungangitshela umbuzo wakho? {current['name']}, you have a question. Can you tell me your question?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        else:
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': "Angiqondi. Ufuna ukubhuka, ushintshe, noma ukubuza? I don't understand. Do you want to book, reschedule, or ask?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
    
    elif step == 4:
        current['details'] = speech_result
        current['step'] = 5
        
        if current['appointment_type'] == 'book':
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {current['name']}. Manje ungangitshela isikhathi ofuna ukuzofika ngaso? Njengamahora angu-9 ekuseni noma ihora lesi-2 emini? Thank you {current['name']}. Now can you tell me what time you want to come? Like 9 AM or 2 PM?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        
        elif current['appointment_type'] == 'reschedule':
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {current['name']}. Manje ungangitshela usuku ofuna ukushintshele kulo? Thank you {current['name']}. Now can you tell me what day you want to change to?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
        
        elif current['appointment_type'] == 'question':
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {current['name']}. Sizokuthumela umbuzo wakho kudokotela. Ungangitshela inombolo yakho yocingo? Thank you {current['name']}. We will send your question to the doctor. Can you tell me your phone number?",
                            'language': 'en-US'
                        }
                    },
                    {
                        'listen': {
                            'speech_timeout': 10
                        }
                    }
                ]
            })
    
    elif step == 5:
        current['final_details'] = speech_result
        
        if current['appointment_type'] == 'book':
            message = f"Ngiyabonga kakhulu {current['name']}! Ubhukile isikhathi sakho ngo{current['details']} ngesikhathi {current['final_details']}. Sizokuthumela umyalezo. Ube nosuku oluhle! Thank you very much {current['name']}! Your appointment is booked for {current['details']} at {current['final_details']}. We will send you a message. Have a nice day!"
        
        elif current['appointment_type'] == 'reschedule':
            message = f"Ngiyabonga {current['name']}. Sizoshintsha isikhathi sakho sibe ngo{current['final_details']}. Sizokuthinta uma kuphelile. Sala kahle! Thank you {current['name']}. We will reschedule your appointment to {current['final_details']}. We will contact you when done. Goodbye!"
        
        elif current['appointment_type'] == 'question':
            message = f"Ngiyabonga {current['name']}. Udokotela uzokuphendula ngombuzo wakho kusasa ngo{current['final_details']}. Ungalindela ucingo. Hamba kahle! Thank you {current['name']}. The doctor will answer your question tomorrow at {current['final_details']}. Expect a call. Goodbye!"
        
        del conversations[call_sid]
        
        return jsonify({
            'actions': [
                {
                    'say': {
                        'speech': message,
                        'language': 'en-US'
                    }
                },
                {
                    'hangup': {}
                }
            ]
        })
    
    return jsonify({
        'actions': [
            {
                'say': {
                    'speech': "Uxolo, ngiyadideka. Ungaqala futhi? Sorry, I'm confused. Can you start again?",
                    'language': 'en-US'
                }
            },
            {
                'listen': {
                    'speech_timeout': 10
                }
            }
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)