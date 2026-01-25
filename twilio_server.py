from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

conversations = {}

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready for conversations"})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    from_number = request.form.get('From', '')
    call_sid = request.form.get('CallSid', '')
    
    speech_result = request.form.get('SpeechResult', '').lower().strip()
    
    print(f"DEBUG: From {from_number} said: '{speech_result}'")
    
    if call_sid not in conversations:
        conversations[call_sid] = {
            'step': 1,
            'name': '',
            'phone': from_number,
            'appointment_type': '',
            'start_time': datetime.now().strftime("%H:%M:%S")
        }
    
    current_convo = conversations[call_sid]
    current_step = current_convo['step']
    
    if current_step == 1:
        current_convo['step'] = 2
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
    
    elif current_step == 2:
        if speech_result:
            current_convo['name'] = speech_result
            current_convo['step'] = 3
            
            name_words = speech_result.split()
            simple_name = "mfowethu"
            for word in name_words:
                if word.lower() not in ['my', 'name', 'is', 'igama', 'lami'] and len(word) > 1:
                    simple_name = word.lower()
                    break
            
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {simple_name}! Ungangitshela ukuthi ufuna ukwenzani? Ungabhuka, ushintshe isikhathi, noma unombuzo? Thank you {simple_name}! Can you tell me what you need? Do you want to book, reschedule, or ask a question?",
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
    
    elif current_step == 3:
        book_words = ['book', 'bhuka', 'ukubhuka', 'ngifuna', 'ngicela', 'booking', 'appointment']
        reschedule_words = ['reschedule', 'change', 'hlela', 'shintsha', 'guqula', 'move']
        question_words = ['question', 'umbuzo', 'buzo', 'ndaba', 'ask', 'help']
        
        if any(word in speech_result for word in book_words):
            current_convo['appointment_type'] = 'book'
            current_convo['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': "Ufuna ukubhuka isikhathi. Ungangitshela usuku ofuna ukuzofika ngalo? Like Monday or Tuesday? You want to book an appointment. Can you tell me what date you want to come?",
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
            current_convo['appointment_type'] = 'reschedule'
            current_convo['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': "Ufuna ukushintsha isikhathi. Ungangitshela igama lakho noma inombolo yesikhathi sakho? You want to reschedule. Can you tell me your name or appointment number?",
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
            current_convo['appointment_type'] = 'question'
            current_convo['step'] = 4
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': "Ufuna ukubuza umbuzo. Ungangitshela umbuzo wakho? You have a question. Can you tell me your question?",
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
                            'speech': "Angizwanga kahle. Ufuna ukubhuka, ushintshe, noma ukubuza? I didn't understand. Do you want to book, reschedule, or ask?",
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
    
    elif current_step == 4:
        app_type = current_convo['appointment_type']
        name = current_convo.get('name', 'mfowethu')
        
        if app_type == 'book':
            current_convo['step'] = 5
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {name}. Ungangitshela isikhathi ofuna ukuzofika ngaso? Njengamahora angu-9 ekuseni noma ihora lesi-2 emini? Thank you {name}. Can you tell me what time you want to come? Like 9 AM or 2 PM?",
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
        
        elif app_type == 'reschedule':
            current_convo['date_info'] = speech_result
            current_convo['step'] = 5
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {name}. Manje ungangitshela isikhathi ofuna ukushintshele kuso? Thank you {name}. Now can you tell me what time you want to change to?",
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
        
        elif app_type == 'question':
            current_convo['question'] = speech_result
            current_convo['step'] = 5
            return jsonify({
                'actions': [
                    {
                        'say': {
                            'speech': f"Ngiyabonga {name}. Ungangitshela inombolo yakho yocingo ukuze sikuthintele? Thank you {name}. Can you tell me your phone number to contact you?",
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
    
    elif current_step == 5:
        app_type = current_convo['appointment_type']
        name = current_convo.get('name', 'mfowethu')
        
        if app_type == 'book':
            current_convo['time_info'] = speech_result
            response_text = f"Ngiyabonga kakhulu {name}! Ubhukile isikhathi sakho. Sizokuthumela imeyili noma umyalezo ngesikhathi. Ube nosuku oluhle! Thank you very much {name}! Your appointment is booked. We will send you an email or message with the time. Have a nice day!"
        
        elif app_type == 'reschedule':
            current_convo['time_info'] = speech_result
            response_text = f"Ngiyabonga {name}. Sizoshintsha isikhathi sakho. Sizokuthinta ngocingo uma kuphelile. Sala kahle! Thank you {name}. We will reschedule your appointment. We will call you when it's done. Goodbye!"
        
        elif app_type == 'question':
            current_convo['phone_info'] = speech_result
            response_text = f"Ngiyabonga {name}. Udokotela uzokuphendula ngombuzo wakho. Ungalindela ucingo kusasa. Hamba kahle! Thank you {name}. The doctor will answer your question. Expect a call tomorrow. Goodbye!"
        
        if call_sid in conversations:
            print(f"DEBUG: Completed conversation for {name}: {app_type}")
            del conversations[call_sid]
        
        return jsonify({
            'actions': [
                {
                    'say': {
                        'speech': response_text,
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
                    'speech': "Uxolo, ngiyadideka. Ungaqala futhi? Sawubona! Sorry, I'm confused. Can you start again? Hello!",
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