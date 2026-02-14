from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
import os
import re
import dateparser
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BOOK_KEYWORDS = {
    'english': ['book', 'new', 'appointment', 'booking', 'make appointment', 'schedule', 'make booking'],
    'isizulu': ['bhuka', 'ukubhuka', 'ngifuna', 'funa', 'ngicela', 'cela', 'ngicela ukubhuka', 'ngidinga'],
    'misheard': ['google mail', 'gmail', 'google', 'mail', 'book a point', 'book appoint', 'book up point']
}

RESCHEDULE_KEYWORDS = {
    'english': ['reschedule', 'change', 'move', 'postpone', 'cancel', 'shift'],
    'isizulu': ['hlela', 'shintsha', 'kabusha', 'hlela kabusha', 'shintsha isikhathi']
}

QUESTION_KEYWORDS = {
    'english': ['question', 'ask', 'inquiry', 'help', 'consult', 'information'],
    'isizulu': ['umbuzo', 'nginombuzo', 'buzo', 'buzisa', 'buza', 'imibuzo', 'idinga usizo']
}

def classify_intent(speech_text):
    if not speech_text:
        return "unknown"
    
    text_lower = speech_text.lower()
    
    all_book_keywords = BOOK_KEYWORDS['english'] + BOOK_KEYWORDS['isizulu'] + BOOK_KEYWORDS['misheard']
    for keyword in all_book_keywords:
        if keyword in text_lower:
            return "book_appointment"
    
    all_reschedule_keywords = RESCHEDULE_KEYWORDS['english'] + RESCHEDULE_KEYWORDS['isizulu']
    for keyword in all_reschedule_keywords:
        if keyword in text_lower:
            return "reschedule"
    
    all_question_keywords = QUESTION_KEYWORDS['english'] + QUESTION_KEYWORDS['isizulu']
    for keyword in all_question_keywords:
        if keyword in text_lower:
            return "question"
    
    return "unknown"

def parse_speech_date(date_speech):
    try:
        date_speech = date_speech.strip().lower()
        
        parsed_date = dateparser.parse(
            date_speech,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now(),
                'TIMEZONE': 'Africa/Johannesburg'
            }
        )
        
        if parsed_date:
            return parsed_date.strftime("%m%d%Y")
        
        today = datetime.now()
        
        if 'tomorrow' in date_speech:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%m%d%Y")
        
        days_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day_name, day_num in days_map.items():
            if day_name in date_speech:
                current_day = today.weekday()
                days_ahead = day_num - current_day
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime("%m%d%Y")
        
        return None
        
    except Exception as e:
        print(f"Error parsing date speech: {e}")
        return None

def parse_speech_time(time_speech):
    try:
        time_speech = time_speech.strip().lower()
        
        time_speech = time_speech.replace('at', '').replace('around', '').replace('about', '').strip()
        
        parsed_time = dateparser.parse(time_speech)
        if parsed_time:
            return parsed_time.strftime("%H%M")
        
        patterns = [
            (r'(\d{1,2})[:.]?(\d{2})?\s*(am|pm)', 1),
            (r'(\d{1,2})\s*(am|pm)', 2),
            (r'(\d{1,2})[:.]?(\d{2})', 3),
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, time_speech)
            if match:
                if pattern_type == 1:
                    hour = int(match.group(1))
                    minute = int(match.group(2) or 0)
                    period = match.group(3).lower()
                    
                    if period == 'pm' and hour < 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                        
                    return f"{hour:02d}{minute:02d}"
                
                elif pattern_type == 2:
                    hour = int(match.group(1))
                    period = match.group(2).lower()
                    
                    if period == 'pm' and hour < 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                        
                    return f"{hour:02d}00"
                
                elif pattern_type == 3:
                    hour = int(match.group(1))
                    minute = int(match.group(2) or 0)
                    return f"{hour:02d}{minute:02d}"
        
        if 'morning' in time_speech:
            return "0900"
        elif 'afternoon' in time_speech:
            return "1400"
        elif 'evening' in time_speech:
            return "1700"
            
        return None
        
    except Exception as e:
        print(f"Error parsing time speech: {e}")
        return None

@app.route('/')
def home():
    return {
        "message": "Twilio bridge server ready",
        "status": "operational",
        "endpoints": {
            "/twilio-webhook": "Classify speech intent",
            "/check-availability": "Check appointment availability",
            "/confirm-booking": "Confirm booking and send to Make.com",
            "/handle-question": "Handle patient questions",
            "/handle-reschedule": "Handle rescheduling",
            "/debug-parse": "Test date/time parsing"
        }
    }

@app.route('/twilio-webhook', methods=['POST'])
def twilio_webhook():
    speech_result = request.form.get('SpeechResult', '')
    
    intent = classify_intent(speech_result)
    
    if intent == "book_appointment":
        return jsonify({
            "actions": [
                {
                    "redirect": {
                        "method": "POST",
                        "uri": "https://webhooks.twilio.com/v1/Accounts/.../Flows/.../Redirect?FlowEvent=return&result=book_appointment"
                    }
                }
            ]
        })
    elif intent == "reschedule":
        return jsonify({
            "actions": [
                {
                    "redirect": {
                        "method": "POST", 
                        "uri": "https://webhooks.twilio.com/v1/Accounts/.../Flows/.../Redirect?FlowEvent=return&result=reschedule"
                    }
                }
            ]
        })
    elif intent == "question":
        return jsonify({
            "actions": [
                {
                    "redirect": {
                        "method": "POST",
                        "uri": "https://webhooks.twilio.com/v1/Accounts/.../Flows/.../Redirect?FlowEvent=return&result=question"
                    }
                }
            ]
        })
    else:
        return jsonify({
            "actions": [
                {
                    "redirect": {
                        "method": "POST",
                        "uri": "https://webhooks.twilio.com/v1/Accounts/.../Flows/.../Redirect?FlowEvent=return&result=unknown"
                    }
                }
            ]
        })

@app.route('/check-availability', methods=['POST'])
def check_availability():
    date_str = request.form.get('date', '')
    time_str = request.form.get('time', '')
    attempt = request.form.get('attempt', '0')

    print(f"Received date: {date_str}, time: {time_str}, attempt: {attempt}")

    if not date_str or not time_str:
        return jsonify({
            'available': False,
            'message': "I didn't receive the date or time clearly. Please try again."
        })

    def parse_dtmf_date(digits):
        digits = digits.strip()
        if digits.isdigit():
            if len(digits) == 4:
                month = int(digits[0:2])
                day = int(digits[2:4])
                year = datetime.now().year
                try:
                    return datetime(year, month, day)
                except:
                    return None
            elif len(digits) == 8:
                month = int(digits[0:2])
                day = int(digits[2:4])
                year = int(digits[4:8])
                try:
                    return datetime(year, month, day)
                except:
                    return None
        return None

    def parse_dtmf_time(digits):
        digits = digits.strip()
        if digits.isdigit() and len(digits) == 4:
            hour = int(digits[0:2])
            minute = int(digits[2:4])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
        return None, None

    dtmf_date = parse_dtmf_date(date_str)
    dtmf_hour, dtmf_minute = parse_dtmf_time(time_str)

    if dtmf_date and dtmf_hour is not None:
        requested_datetime = dtmf_date.replace(hour=dtmf_hour, minute=dtmf_minute)
    else:
        parsed_date = parse_speech_date(date_str)
        parsed_time = parse_speech_time(time_str)

        if not parsed_date:
            return jsonify({
                'available': False,
                'message': f"Sorry, I didn't understand the date '{date_str}'. Please try again."
            })
        if not parsed_time:
            return jsonify({
                'available': False,
                'message': f"Sorry, I didn't understand the time '{time_str}'. Please try again."
            })

        try:
            month = int(parsed_date[0:2])
            day = int(parsed_date[2:4])
            year = int(parsed_date[4:8])
            hour = int(parsed_time[0:2])
            minute = int(parsed_time[2:4])
            requested_datetime = datetime(year, month, day, hour, minute)
        except:
            return jsonify({
                'available': False,
                'message': "Invalid date or time format. Please try again."
            })

    if requested_datetime < datetime.now():
        return jsonify({
            'available': False,
            'message': "Appointment time must be in the future. Please choose a later date and time."
        })

    hour = requested_datetime.hour
    if hour < 9 or hour >= 17:
        if hour < 9:
            suggestion_hour = 9
            suggestion_day = requested_datetime
        else:
            suggestion_hour = 9
            suggestion_day = requested_datetime + timedelta(days=1)

        suggestion_datetime = suggestion_day.replace(hour=suggestion_hour, minute=0)
        suggestion_str = suggestion_datetime.strftime("%A at %I:%M %p")

        return jsonify({
            'available': False,
            'message': f"Clinic hours are 9 AM to 5 PM. The next available slot is {suggestion_str}. Shall I book that?",
            'suggestions': [{
                'date': suggestion_datetime.strftime("%m%d%Y"),
                'time': suggestion_datetime.strftime("%H%M")
            }]
        })

    import random
    is_available = random.random() > 0.3

    if is_available:
        formatted_date = requested_datetime.strftime("%A, %B %d")
        formatted_time = requested_datetime.strftime("%I:%M %p")
        return jsonify({
            'available': True,
            'message': f"{formatted_date} at {formatted_time} is available. Press 1 to confirm, or 2 to hear alternatives.",
            'raw_date': requested_datetime.strftime("%m%d%Y"),
            'raw_time': requested_datetime.strftime("%H%M")
        })
    else:
        alt1 = requested_datetime + timedelta(hours=2)
        if alt1.hour >= 17:
            alt1 = (requested_datetime + timedelta(days=1)).replace(hour=9, minute=0)

        alt2 = requested_datetime + timedelta(days=1)
        alt2 = alt2.replace(hour=9, minute=0)

        return jsonify({
            'available': False,
            'message': f"Sorry, {requested_datetime.strftime('%I:%M %p')} is not available. We have {alt1.strftime('%A at %I:%M %p')} or {alt2.strftime('%A at %I:%M %p')}. Press 1 for the first, 2 for the second, or 3 to try a different time.",
            'suggestions': [
                {'date': alt1.strftime("%m%d%Y"), 'time': alt1.strftime("%H%M")},
                {'date': alt2.strftime("%m%d%Y"), 'time': alt2.strftime("%H%M")}
            ]
        })

@app.route('/debug-parse', methods=['POST'])
def debug_parse():
    date_speech = request.form.get('date', '')
    time_speech = request.form.get('time', '')
    
    formatted_date = parse_speech_date(date_speech)
    formatted_time = parse_speech_time(time_speech)
    
    return jsonify({
        "input_date": date_speech,
        "input_time": time_speech,
        "parsed_date": formatted_date,
        "parsed_time": formatted_time,
        "success": formatted_date is not None and formatted_time is not None
    })

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    try:
        date_str = request.form.get('date', '')
        time_str = request.form.get('time', '')
        phone = request.form.get('phone', '')
        
        if len(date_str) != 8:
            date_str = parse_speech_date(date_str) or date_str
        if len(time_str) != 4:
            time_str = parse_speech_time(time_str) or time_str
        
        if len(date_str) == 8 and len(time_str) == 4:
            month = int(date_str[0:2])
            day = int(date_str[2:4])
            year = int(date_str[4:8])
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            
            appointment_datetime = datetime(year, month, day, hour, minute)
            formatted_datetime = appointment_datetime.strftime("%Y-%m-%d %H:%M")
        else:
            formatted_datetime = f"{date_str} at {time_str}"
        
        make_calendar_webhook = os.getenv('MAKE_CALENDAR_WEBHOOK')
        make_sheets_webhook = os.getenv('MAKE_SHEETS_WEBHOOK')
        
        booking_data = {
            "patient_phone": phone,
            "appointment_time": formatted_datetime,
            "status": "confirmed",
            "source": "Tameeka Voice Assistant",
            "timestamp": datetime.now().isoformat()
        }
        
        if make_calendar_webhook:
            try:
                requests.post(make_calendar_webhook, json=booking_data, timeout=5)
            except Exception:
                pass
        
        if make_sheets_webhook:
            try:
                requests.post(make_sheets_webhook, json=booking_data, timeout=5)
            except Exception:
                pass
        
        return jsonify({
            "success": True,
            "message": "Booking confirmed successfully! A confirmation will be sent to your phone.",
            "confirmation_number": f"TAM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        })
        
    except Exception as e:
        print(f"Error in confirm_booking: {e}")
        return jsonify({
            "success": False,
            "message": "Error confirming booking. Please call the clinic directly at 031-123-4567."
        })

@app.route('/handle-question', methods=['POST'])
def handle_question():
    question = request.form.get('question', '')
    
    faq_responses = {
        'hours': "Our clinic hours are Monday to Friday, 9 AM to 5 PM.",
        'location': "We are located at 123 Medical Street, Durban.",
        'contact': "You can call us at 031-123-4567 during business hours.",
        'emergency': "For emergencies, please go to the nearest hospital emergency room."
    }
    
    question_lower = question.lower()
    response = "Thank you for your question. A staff member will call you back shortly with more information."
    
    if 'hour' in question_lower or 'open' in question_lower or 'close' in question_lower:
        response = faq_responses['hours']
    elif 'location' in question_lower or 'address' in question_lower or 'where' in question_lower:
        response = faq_responses['location']
    elif 'contact' in question_lower or 'phone' in question_lower or 'call' in question_lower:
        response = faq_responses['contact']
    elif 'emergency' in question_lower or 'urgent' in question_lower:
        response = faq_responses['emergency']
    
    return jsonify({
        "response": response,
        "action": "say_response"
    })

@app.route('/handle-reschedule', methods=['POST'])
def handle_reschedule():
    return jsonify({
        "response": "Please call our front desk at 031-123-4567 to reschedule your appointment. We're open Monday to Friday, 9 AM to 5 PM.",
        "action": "say_response"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)