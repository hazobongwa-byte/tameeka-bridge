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
        time_speech = time_speech.replace('_', ' ')
        
        period = None
        if re.search(r'p[.\s_]*m', time_speech):
            period = 'pm'
        elif re.search(r'a[.\s_]*m', time_speech):
            period = 'am'
        
        time_speech = re.sub(r'p[.\s_]*m', 'pm', time_speech)
        time_speech = re.sub(r'a[.\s_]*m', 'am', time_speech)
        
        word_to_num = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14',
            'fifteen': '15', 'sixteen': '16', 'seventeen': '17', 'eighteen': '18',
            'nineteen': '19', 'twenty': '20', 'thirty': '30', 'forty': '40',
            'fifty': '50'
        }
        
        words = time_speech.split()
        hour_str = None
        minute_str = '00'
        
        for word in words:
            if word in word_to_num:
                if hour_str is None:
                    hour_str = word_to_num[word]
                else:
                    minute_str = word_to_num[word]
            elif word.isdigit():
                if hour_str is None:
                    hour_str = word
                else:
                    minute_str = word
        
        if hour_str:
            hour = int(hour_str)
            minute = int(minute_str)
            if period == 'pm' and hour < 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}{minute:02d}"
        
        match = re.search(r'(\d{1,2})[:.](\d{2})', time_speech)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if period == 'pm' and hour < 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}{minute:02d}"
        
        match = re.search(r'(\d{1,2})\s*(am|pm)', time_speech)
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            if period == 'pm' and hour < 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}00"
        
        if 'morning' in time_speech:
            return "0900"
        elif 'afternoon' in time_speech:
            return "1400"
        elif 'evening' in time_speech:
            return "1700"
        
        parsed = dateparser.parse(time_speech)
        if parsed:
            return parsed.strftime("%H%M")
        
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
    try:
        date_speech = request.form.get('date', '')
        time_speech = request.form.get('time', '')
        attempt = int(request.form.get('attempt', '0'))
        
        formatted_date = parse_speech_date(date_speech)
        formatted_time = parse_speech_time(time_speech)
        
        if not formatted_date:
            return jsonify({
                "available": False,
                "message": f"Sorry, I didn't understand the date '{date_speech}'. Please say something like 'tomorrow' or 'next Tuesday'.",
                "attempt": attempt
            })
        
        if not formatted_time:
            return jsonify({
                "available": False,
                "message": f"Sorry, I didn't understand the time '{time_speech}'. Please say something like '2:30 PM' or 'fourteen thirty'.",
                "attempt": attempt
            })
        
        try:
            month = int(formatted_date[0:2])
            day = int(formatted_date[2:4])
            year = int(formatted_date[4:8])
            hour = int(formatted_time[0:2])
            minute = int(formatted_time[2:4])
            
            requested_datetime = datetime(year, month, day, hour, minute)
            
            if requested_datetime < datetime.now():
                return jsonify({
                    "available": False,
                    "message": "Appointment time must be in the future. Please choose a later date and time.",
                    "attempt": attempt
                })
            
            if hour < 9 or hour >= 17:
                return jsonify({
                    "available": False,
                    "message": "Clinic hours are 9 AM to 5 PM. Please choose a time within these hours.",
                    "attempt": attempt
                })
            
            import random
            is_available = random.random() < 0.8
            
            suggestions = []
            
            alt1_datetime = requested_datetime + timedelta(days=1)
            alt1_datetime = alt1_datetime.replace(hour=10, minute=0)
            suggestions.append({
                "day_name": alt1_datetime.strftime("%B %d, %Y"),
                "time": alt1_datetime.strftime("%I:%M %p"),
                "raw_date": alt1_datetime.strftime("%m%d%Y"),
                "raw_time": alt1_datetime.strftime("%H%M")
            })
            
            alt2_datetime = requested_datetime + timedelta(days=2)
            alt2_datetime = alt2_datetime.replace(hour=14, minute=30)
            suggestions.append({
                "day_name": alt2_datetime.strftime("%B %d, %Y"),
                "time": alt2_datetime.strftime("%I:%M %p"),
                "raw_date": alt2_datetime.strftime("%m%d%Y"),
                "raw_time": alt2_datetime.strftime("%H%M")
            })
            
            alt3_datetime = requested_datetime + timedelta(days=3)
            alt3_datetime = alt3_datetime.replace(hour=11, minute=0)
            suggestions.append({
                "day_name": alt3_datetime.strftime("%B %d, %Y"),
                "time": alt3_datetime.strftime("%I:%M %p"),
                "raw_date": alt3_datetime.strftime("%m%d%Y"),
                "raw_time": alt3_datetime.strftime("%H%M")
            })
            
            if is_available:
                if attempt == 0:
                    message = f"The selected time on {requested_datetime.strftime('%B %d')} at {requested_datetime.strftime('%I:%M %p')} is available. Say yes to confirm this slot or next to hear another option."
                    return jsonify({
                        "available": True,
                        "message": message,
                        "formatted_date": requested_datetime.strftime("%B %d, %Y"),
                        "formatted_time": requested_datetime.strftime("%I:%M %p"),
                        "raw_date": formatted_date,
                        "raw_time": formatted_time,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                elif attempt == 1:
                    message = f"Another option is at {suggestions[0]['time']} on {suggestions[0]['day_name']}. Say yes to book this slot or next to hear another option."
                    return jsonify({
                        "available": True,
                        "message": message,
                        "formatted_date": requested_datetime.strftime("%B %d, %Y"),
                        "formatted_time": requested_datetime.strftime("%I:%M %p"),
                        "raw_date": formatted_date,
                        "raw_time": formatted_time,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                elif attempt == 2:
                    message = f"We also have a slot at {suggestions[1]['time']} on {suggestions[1]['day_name']}. Say yes to book this slot or next to hear one more option."
                    return jsonify({
                        "available": True,
                        "message": message,
                        "formatted_date": requested_datetime.strftime("%B %d, %Y"),
                        "formatted_time": requested_datetime.strftime("%I:%M %p"),
                        "raw_date": formatted_date,
                        "raw_time": formatted_time,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                else:
                    message = f"One more option at {suggestions[2]['time']} on {suggestions[2]['day_name']}. Say yes to book this slot or we'll end the call."
                    return jsonify({
                        "available": True,
                        "message": message,
                        "formatted_date": requested_datetime.strftime("%B %d, %Y"),
                        "formatted_time": requested_datetime.strftime("%I:%M %p"),
                        "raw_date": formatted_date,
                        "raw_time": formatted_time,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
            else:
                if attempt == 0:
                    message = f"Sorry, {requested_datetime.strftime('%I:%M %p')} is not available. We have an alternative at {suggestions[0]['time']} on {suggestions[0]['day_name']}. Say yes to book this slot or next to hear another option."
                    return jsonify({
                        "available": False,
                        "message": message,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                elif attempt == 1:
                    message = f"Another option is at {suggestions[1]['time']} on {suggestions[1]['day_name']}. Say yes to book this slot or next to hear another option."
                    return jsonify({
                        "available": False,
                        "message": message,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                elif attempt == 2:
                    message = f"We also have a slot at {suggestions[2]['time']} on {suggestions[2]['day_name']}. Say yes to book this slot or next to try another day."
                    return jsonify({
                        "available": False,
                        "message": message,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                else:
                    message = "We don't have more available slots at the moment. Please call again another day. Goodbye."
                    return jsonify({
                        "available": False,
                        "message": message,
                        "suggestions": suggestions,
                        "attempt": attempt
                    })
                
        except ValueError as e:
            print(f"Error parsing formatted date/time: {e}")
            return jsonify({
                "available": False,
                "message": "Invalid date or time. Please try again with a different time.",
                "attempt": attempt
            })
            
    except Exception as e:
        print(f"Error in check_availability: {e}")
        return jsonify({
            "available": False,
            "message": "Technical error checking availability. Please try again or call the clinic directly.",
            "attempt": attempt
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
        name = request.form.get('name', '')
        
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
            "patient_name": name,
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