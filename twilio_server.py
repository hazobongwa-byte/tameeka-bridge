from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random
import requests
import os

app = Flask(__name__)

appointments = {}

MAKE_CALENDAR_WEBHOOK = os.environ.get('MAKE_CALENDAR_WEBHOOK', '')
MAKE_SHEETS_WEBHOOK = os.environ.get('MAKE_SHEETS_WEBHOOK', '')

def send_to_make_com(appointment_data):
    try:
        calendar_response = requests.post(
            MAKE_CALENDAR_WEBHOOK,
            json={
                "action": "create_calendar_event",
                "appointment_id": appointment_data["appointment_id"],
                "phone": appointment_data["phone"],
                "date": appointment_data["date"],
                "time": appointment_data["time"],
                "timestamp": appointment_data["timestamp"],
                "status": "booked",
                "type": "appointment_booking"
            },
            timeout=5
        )
        
        sheets_response = requests.post(
            MAKE_SHEETS_WEBHOOK,
            json={
                "action": "add_to_sheet",
                "appointment_id": appointment_data["appointment_id"],
                "patient_phone": appointment_data["phone"],
                "appointment_date": appointment_data["date"],
                "appointment_time": appointment_data["time"],
                "booking_timestamp": appointment_data["timestamp"],
                "doctor": "Dr. Ntombela",
                "clinic": "Dr. Ntombela's Clinic",
                "status": "confirmed",
                "source": "twilio_voice_assistant"
            },
            timeout=5
        )
        
        return calendar_response.status_code == 200 and sheets_response.status_code == 200
    except Exception as e:
        print(f"Make.com error: {str(e)}")
        return False

@app.route('/')
def home():
    return jsonify({"message": "Twilio bridge server ready", "status": "operational"})

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    speech_result = request.form.get('SpeechResult', '')
    body_data = request.form.get('body', '')
    
    if not speech_result and body_data:
        if 'SpeechResult=' in body_data:
            parts = body_data.split('SpeechResult=')
            if len(parts) > 1:
                speech_result = parts[1]
                if '&' in speech_result:
                    speech_result = speech_result.split('&')[0]
    
    speech_result = speech_result.lower().strip() if speech_result else ''
    print(f"DEBUG: Speech received: '{speech_result}'")
    
    if not speech_result:
        print("DEBUG: Speech is EMPTY")
        return jsonify({'action': 'unknown', 'message': 'Please speak clearly'})
    
    book_words = [
        'book', 'new', 'appointment', 'booking', 'make appointment', 'schedule',
        'bhuka', 'ukubhuka', 'ngifuna', 'funa', 'ngicela', 'cela',
        'ngicela ukubhuka', 'ngifuna ukubhuka', 'bhukha', 'ukubhukha',
        'isikhathi', 'bengisacela', 'awungibhukise', 'ungibhukise',
        'yenza i-appointment', 'ngifuna isikhathi',
        'google mail', 'gmail', 'google', 'mail', 'google male',
        'book a point', 'book appoint', 'pointment', 'book a pointment',
        'puka', 'buka', 'booker', 'bookings', 'booked', 'bok', 
        'bok appointment', 'bok a pointment', 'i want to book', 
        'need appointment', 'make booking', 'ngifuna ukwenza', 
        'ngifuna i-appointment', 'funa i-appointment', 'ngicela isikhathi', 
        'cela isikhathi', 'book me', 'appointment please', 'want to book',
        'would like to book', 'need to book', 'looking to book',
        'make a booking', 'set up appointment', 'schedule appointment'
    ]
    
    reschedule_words = [
        'reschedule', 'change', 'move', 'postpone', 'cancel', 'cancel appointment',
        'hlela', 'shintsha', 'kabusha', 'hlela kabusha', 'hlela futhi',
        'guqula', 'shintsha isikhathi', 'shintsha ingqophamlando',
        'bhukha kabusha', 'khansela', 'yekisa', 'rice schedule', 
        're schedule', 're-schedule', 'schedule change', 'change appointment',
        'move appointment', 'different time', 'different date', 'new time',
        'new date', 'postpone appointment', 'delay appointment', 'shift appointment',
        'reschedule my', 'change my', 'move my', 'postpone my', 'cancel my',
        'adjust appointment', 'modify appointment', 'alter appointment'
    ]
    
    question_words = [
        'question', 'ask', 'inquiry', 'help', 'consult', 'advice',
        'umbuzo', 'nginombuzo', 'buzo', 'buzisa', 'buza', 'ndaba', 
        'nginendaba', 'cebisa', 'eluleka', 'xoxa nodokotela', 'kwestion', 
        'quest', 'query', 'inquiry', 'help me', 'need help', 'have a question',
        'want to ask', 'need advice', 'need consultation', 'medical question',
        'ask doctor', 'talk to doctor', 'speak to doctor', 'consult doctor',
        'doctor advice', 'medical advice', 'health question', 'symptom question',
        'inquire', 'enquire', 'seek advice', 'get advice', 'clinical question'
    ]
    
    if any(word in speech_result for word in book_words):
        print("DEBUG: Matched BOOK_APPOINTMENT")
        return jsonify({'action': 'book_appointment', 'message': 'Booking new appointment'})
    elif any(word in speech_result for word in reschedule_words):
        print("DEBUG: Matched RESCHEDULE")
        return jsonify({'action': 'reschedule', 'message': 'Rescheduling appointment'})
    elif any(word in speech_result for word in question_words):
        print("DEBUG: Matched QUESTION")
        return jsonify({'action': 'question', 'message': 'Question for doctor'})
    else:
        print("DEBUG: No match - returning UNKNOWN")
        return jsonify({'action': 'unknown', 'message': 'Please say: book appointment, reschedule, or question'})

@app.route('/check-availability', methods=['POST'])
def check_availability():
    date_str = request.form.get('date', '')
    time_str = request.form.get('time', '')
    
    print(f"DEBUG: Checking availability for {date_str} at {time_str}")
    print(f"DEBUG: Full form data: {request.form}")
    
    if not date_str or not time_str:
        print("ERROR: Date or time is empty!")
        return jsonify({
            'available': True,
            'message': 'Please provide date and time',
            'date': date_str,
            'time': time_str,
            'warning': 'Date or time was empty'
        })
    
    is_available = random.choice([True, True, True, True, True, False])
    
    if is_available:
        print(f"DEBUG: Slot is AVAILABLE")
        return jsonify({
            'available': True,
            'message': f'Slot on {date_str} at {time_str} is available',
            'date': date_str,
            'time': time_str
        })
    else:
        same_day_times = []
        if time_str == "09:00":
            same_day_times = ["10:00", "11:00", "14:00"]
        elif time_str == "10:00":
            same_day_times = ["09:00", "11:00", "15:00"]
        else:
            same_day_times = ["09:00", "10:00", "16:00"]
        
        next_day = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        print(f"DEBUG: Slot NOT available, suggesting alternatives")
        return jsonify({
            'available': False,
            'message': f'Slot on {date_str} at {time_str} is booked',
            'same_day_alternatives': same_day_times,
            'next_available_day': next_day,
            'next_day_slots': ["09:00", "10:00", "11:00", "14:00", "15:00"],
            'suggestion_1': f"{date_str} at {same_day_times[0]}" if same_day_times else f"{next_day} at 09:00",
            'suggestion_2': f"{date_str} at {same_day_times[1]}" if len(same_day_times) > 1 else f"{next_day} at 10:00",
            'suggestion_3': f"{next_day} at 09:00"
        })

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    phone = request.form.get('phone', '')
    date = request.form.get('date', '')
    time = request.form.get('time', '')
    
    print(f"DEBUG: Confirming booking for {phone} on {date} at {time}")
    
    appointment_id = f"APT{random.randint(10000, 99999)}"
    appointment_data = {
        'appointment_id': appointment_id,
        'phone': phone,
        'date': date,
        'time': time,
        'status': 'confirmed',
        'timestamp': datetime.now().isoformat()
    }
    
    appointments[appointment_id] = appointment_data
    
    make_success = False
    if MAKE_CALENDAR_WEBHOOK and MAKE_SHEETS_WEBHOOK:
        make_success = send_to_make_com(appointment_data)
        print(f"DEBUG: Make.com integration: {'Success' if make_success else 'Failed'}")
    
    response_data = {
        'success': True,
        'appointment_id': appointment_id,
        'message': f'Appointment confirmed for {date} at {time}',
        'confirmation': f'Your appointment ID is {appointment_id}.',
        'make_integration_success': make_success
    }
    
    if not make_success and (MAKE_CALENDAR_WEBHOOK or MAKE_SHEETS_WEBHOOK):
        response_data['warning'] = 'Appointment booked but Make.com integration failed'
    
    return jsonify(response_data)

@app.route('/handle-question', methods=['POST'])
def handle_question():
    question = request.form.get('question', '')
    phone = request.form.get('phone', '')
    
    print(f"DEBUG: Question from {phone}: {question}")
    
    return jsonify({
        'success': True,
        'message': 'Question received. Doctor will call you within 24 hours.',
        'response': 'Thank you! The doctor will answer your question. Expect a call soon.'
    })

@app.route('/handle-reschedule', methods=['POST'])
def handle_reschedule():
    original_date = request.form.get('original_date', '')
    original_time = request.form.get('original_time', '')
    new_date = request.form.get('new_date', '')
    new_time = request.form.get('new_time', '')
    phone = request.form.get('phone', '')
    
    print(f"DEBUG: Rescheduling from {original_date} {original_time} to {new_date} {new_time}")
    
    return jsonify({
        'success': True,
        'message': f'Appointment rescheduled to {new_date} at {new_time}',
        'confirmation': f'Your appointment has been moved to {new_date} at {new_time}.'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)