@app.route('/check-availability', methods=['POST'])
def check_availability():
    try:
        date_speech = request.form.get('date', '')
        time_speech = request.form.get('time', '')
        
        formatted_date = parse_speech_date(date_speech)
        formatted_time = parse_speech_time(time_speech)
        
        if not formatted_date:
            return jsonify({
                "available": False,
                "message": f"Sorry, I didn't understand the date '{date_speech}'. Please say something like 'tomorrow' or 'next Tuesday'."
            })
        
        if not formatted_time:
            return jsonify({
                "available": False,
                "message": f"Sorry, I didn't understand the time '{time_speech}'. Please say something like '2:30 PM' or 'fourteen thirty'."
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
                    "message": "Appointment time must be in the future. Please choose a later date and time."
                })
            
            if hour < 9 or hour >= 17:
                return jsonify({
                    "available": False,
                    "message": "Clinic hours are 9 AM to 5 PM. Please choose a time within these hours."
                })
            
            import random
            is_available = random.random() > 0.2
            
            suggestions = []
            
            # Suggestion 1: Same day, 2 hours later
            alt1_hour = hour + 2
            if alt1_hour >= 17:
                alt1_hour = 9
                alt1_datetime = requested_datetime + timedelta(days=1)
            else:
                alt1_datetime = requested_datetime.replace(hour=alt1_hour)
            
            suggestion1 = {
                "day_name": alt1_datetime.strftime("%B %d, %Y"),
                "time": alt1_datetime.strftime("%I:%M %p"),
                "raw_date": alt1_datetime.strftime("%m%d%Y"),
                "raw_time": alt1_datetime.strftime("%H%M")
            }
            suggestions.append(suggestion1)
            
            # Suggestion 2: Next day, same time
            alt2_datetime = requested_datetime + timedelta(days=1)
            suggestion2 = {
                "day_name": alt2_datetime.strftime("%B %d, %Y"),
                "time": alt2_datetime.strftime("%I:%M %p"),
                "raw_date": alt2_datetime.strftime("%m%d%Y"),
                "raw_time": alt2_datetime.strftime("%H%M")
            }
            suggestions.append(suggestion2)
            
            if is_available:
                return jsonify({
                    "available": True,
                    "message": f"The selected time on {requested_datetime.strftime('%B %d')} at {requested_datetime.strftime('%I:%M %p')} is available. Please confirm your booking.",
                    "formatted_date": requested_datetime.strftime("%B %d, %Y"),
                    "formatted_time": requested_datetime.strftime("%I:%M %p"),
                    "raw_date": formatted_date,
                    "raw_time": formatted_time,
                    "suggestions": suggestions
                })
            else:
                return jsonify({
                    "available": False,
                    "message": f"Sorry, {requested_datetime.strftime('%I:%M %p')} is not available. Would you like to try {suggestion1['time']} or {suggestion2['time']} instead?",
                    "suggestions": suggestions
                })
                
        except ValueError as e:
            print(f"Error parsing formatted date/time: {e}")
            return jsonify({
                "available": False,
                "message": "Invalid date or time. Please try again with a different time."
            })
            
    except Exception as e:
        print(f"Error in check_availability: {e}")
        return jsonify({
            "available": False,
            "message": "Technical error checking availability. Please try again or call the clinic directly."
        })