from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS
# from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Load environment variables from .env file
# load_dotenv()

# Fixed sender and recipient email details
SENDER_EMAIL = "pernetiyeswanthkumar@gmail.com"
SENDER_PASSWORD = "jlzo vwnx itbh coxv" #App password
RECIPIENT_EMAIL = "phrudayacharihruday@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Create Flask app with custom static and template folders
app = Flask(__name__,
            static_folder='static',  # Custom location for static files
            template_folder='templates')  # Custom location for templates

CORS(app)  # Enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ev_vehicle = db.Column(db.String(100), nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    drop_location = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pending')

# Create tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard1.html')  # Assuming dashboard.html is in assets/templates

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        ev_vehicle = data['ev_vehicle']
        pickup_location = data['pickup_location_id']
        drop_location = data['drop_location_id']

        # Create new booking record with "Confirmed" status
        new_booking = Booking(
            ev_vehicle=ev_vehicle,
            pickup_location=pickup_location,
            drop_location=drop_location,
            status='Confirmed'  # Set default status to Confirmed
        )
        db.session.add(new_booking)
        db.session.commit()

        # Email content
        subject = "New Service Request"
        body = (
            f"Dear Driver,\n\n"
            f"A new service request has been submitted.\n\n"
            f"Details:\n"
            f"Booking ID: #{new_booking.id}\n"
            f"EV Vehicle: {ev_vehicle}\n"
            f"Pickup Location: {pickup_location}\n"
            f"Drop Location: {drop_location}\n"
            f"Status: Confirmed\n\n"
            f"Please proceed to fulfill this request.\n\n"
            f"Thank you."
        )

        # Send email to driver
        msg_driver = MIMEText(body)
        msg_driver["Subject"] = subject
        msg_driver["From"] = SENDER_EMAIL
        msg_driver["To"] = RECIPIENT_EMAIL

        # Send email to user (if logged in)
        if 'user_email' in session:  # Assuming you store user's email in session after Google login
            user_body = (
                f"Dear User,\n\n"
                f"Your service request has been confirmed.\n\n"
                f"Booking Details:\n"
                f"Booking ID: #{new_booking.id}\n"
                f"EV Vehicle: {ev_vehicle}\n"
                f"Pickup Location: {pickup_location}\n"
                f"Drop Location: {drop_location}\n"
                f"Status: Confirmed\n\n"
                f"Thank you for using our service!"
            )
            
            msg_user = MIMEText(user_body)
            msg_user["Subject"] = "Your Booking Confirmation"
            msg_user["From"] = SENDER_EMAIL
            msg_user["To"] = session['user_email']

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg_driver.as_string())
            
            if 'user_email' in session:
                server.sendmail(SENDER_EMAIL, session['user_email'], msg_user.as_string())

        return jsonify({"message": "Booking confirmed and emails sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_driver_location')
def get_driver_location():
    # For testing, return dummy coordinates
    # In production, this would fetch real driver location data
    return jsonify({
        'latitude': 9.55,
        'longitude': 77.7
    })

@app.route('/booking-history')
def booking_history():
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('booking_history.html', bookings=bookings)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login2'))

@app.route('/login')
def login2():
    return render_template('login.html')

# @app.route('/store-user-session', methods=['POST'])
# def store_user_session():
#     try:
#         user_data = request.json
        
#         # Store user data in session
#         session['user_email'] = user_data['email']
#         session['user_name'] = user_data['displayName']
#         session['user_id'] = user_data['uid']
        
#         return jsonify({'success': True}), 200
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/change-password')
def change_password():
    # Check if user is logged in
    # if 'user_email' not in session:
    #     return redirect(url_for('login2'))
    return render_template('changepass.html')

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})

    try:
        data = request.json
        current_password = data['currentPassword']
        new_password = data['newPassword']
        confirm_password = data['confirmPassword']

        # Add your password validation logic here
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'})

        # Add password strength validation
        if len(new_password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'})

        # Here you would typically verify the current password and update it in your database
        # For this example, we'll just return success
        return jsonify({'success': True, 'message': 'Password updated successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
