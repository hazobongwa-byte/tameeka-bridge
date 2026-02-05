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
            
            alt1_hour = hour + 2
            alt1_day = day
            alt1_month = month
            alt1_year = year
            
            if alt1_hour >= 17:
                alt1_hour = 9
                alt1_datetime = requested_datetime + timedelta(days=1)
                alt1_day = alt1_datetime.day
                alt1_month = alt1_datetime.month
                alt1_year = alt1_datetime.year
            
            suggestion1_time = f"{alt1_hour:02d}:{minute:02d}"
            suggestion1_time_12hr = datetime(alt1_year, alt1_month, alt1_day, alt1_hour, minute).strftime("%I:%M %p")
            suggestion1_date = datetime(alt1_year, alt1_month, alt1_day).strftime("%B %d, %Y")
            
            suggestions.append({
                "day_name": suggestion1_date,
                "time": suggestion1_time_12hr,
                "raw_date": f"{alt1_month:02d}{alt1_day:02d}{alt1_year}",
                "raw_time": f"{alt1_hour:02d}{minute:02d}"
            })
            
            alt2_datetime = requested_datetime + timedelta(days=1)
            suggestion2_time_12hr = alt2_datetime.strftime("%I:%M %p")
            suggestion2_date = alt2_datetime.strftime("%B %d, %Y")
            
            suggestions.append({
                "day_name": suggestion2_date,
                "time": suggestion2_time_12hr,
                "raw_date": alt2_datetime.strftime("%m%d%Y"),
                "raw_time": alt2_datetime.strftime("%H%M")
            })
            
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
                    "message": f"Sorry, {requested_datetime.strftime('%I:%M %p')} is not available. Would you like to try {suggestion1_time_12hr} or {suggestion2_time_12hr} instead?",
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