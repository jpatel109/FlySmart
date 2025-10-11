# 📌 Import required modules
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, request 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from datetime import datetime, timedelta 
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message 
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta 
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import mysql.connector
import speech_recognition as sr
import pyttsx3
import pymysql
import random, string
import os, re
import pandas as pd
import requests
import traceback
import json


# ✅ Fix Circular Import
pymysql.install_as_MySQLdb()

# 📌 Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'flysmart360@gmail.com'
app.config['MAIL_PASSWORD'] = 'ubot umev dlsk ckch'
app.config['MAIL_DEFAULT_SENDER'] = ('FlySmart', 'flysmart360@gmail.com')

mail = Mail(app)

# ✅ Configure Flask-Mail 
def send_confirmation_email(
    recipient_email,
    ticket_id,
    flight_number,
    total_price,
    airline,
    departure,
    arrival,
    departure_time,
    arrival_time,
    seat_preference,
    meal_option,
    flight_class,
    base_fare,
    tax,
    addon_total,
    passenger_name,
    addon_items  # ✅ New parameter
):
    import traceback

    print("📤 Attempting to send confirmation email...")
    print(f"Recipient email: {recipient_email}")
    print(f"🎫 Add-on items: {addon_items}")  # ✅ Log for debugging

    subject = "Your FlySmart Booking Confirmation"

    try:
        # ✅ Render HTML email with all values
        html_body = render_template(
            'email_template.html',
            ticket_id=ticket_id,
            flight_number=flight_number,
            total_price=total_price,
            airline=airline,
            departure=departure,
            arrival=arrival,
            departure_time=departure_time,
            arrival_time=arrival_time,
            seat_preference=seat_preference,
            meal_option=meal_option,
            flight_class=flight_class,
            base_fare=base_fare,
            tax=tax,
            addon_total=addon_total,
            passenger_name=passenger_name,
            addon_items=addon_items  # ✅ Include in template
        )

        print("📧 Rendered HTML body successfully.")
        print("------ EMAIL BODY START ------")
        print(html_body)
        print("------ EMAIL BODY END ------")

        # ✅ Send the email
        msg = Message(subject=subject, recipients=[recipient_email], html=html_body)
        print("📨 Sending email now...")
        mail.send(msg)

        print(f"✅ Email successfully sent to: {recipient_email}")

        # ✅ Log action
        log = SystemLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=f"Sent booking confirmation email to {recipient_email}"
        )
        db.session.add(log)
        db.session.commit()

    except Exception as e:
        print(f"❌ Exception occurred while sending email to {recipient_email}: {e}")
        traceback.print_exc()



# ✅ Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456789@localhost/flysmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY'] = '6Lcc7CcrAAAAALOreMMi1SJCdJz54MPVZ87a-yx8' # Required for CSRF protection

app.secret_key = '6Lcc7CcrAAAAALOreMMi1SJCdJz54MPVZ87a-yx8'  # Required for flash messages

# ✅ Initialize Database & Bcrypt
db = SQLAlchemy(app)  
bcrypt = Bcrypt(app)  

# ✅ Initialize Flask-Migrate
migrate = Migrate(app, db)  # ✅ Make sure this is after db = SQLAlchemy(app)

# ✅ Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ✅ **Database Model for Users**
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    role = db.Column(db.String(10), default='User')
    profile_pic = db.Column(db.String(200), default='default.png')

    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    
    # ✅ New fields for Account Settings
    enable_2fa = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


# ✅ **Flask-Login User Loader**
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ✅ **Database Model for Bookings**
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False) 
    passenger_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    flight_class = db.Column(db.String(20), nullable=False)
    addons = db.Column(db.Text)  # comma-separated values for add-ons
    total_price = db.Column(db.Float, nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Used for sorting past bookings
    ticket_id = db.Column(db.String(100), unique=True, nullable=True)  # Unique ticket ID

    user = db.relationship('User', backref=db.backref('search_logs', passive_deletes=True))
    flight = db.relationship('Flight', backref='bookings')


    def __repr__(self):
        return f"<Booking {self.id} for {self.passenger_name}>"


# 📌 **Database Model for Flights**
class Flight(db.Model):
    __tablename__ = "flight"

    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(100), unique=True, nullable=False)
    departure = db.Column(db.String(100), nullable=False, index=True)
    arrival = db.Column(db.String(100), nullable=False, index=True) 
    price = db.Column(db.DECIMAL(10, 2), nullable=False) 
    available_seats = db.Column(db.Integer, nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    arrival_time = db.Column(db.DateTime, nullable=False) 
    duration = db.Column(db.String(20), nullable=True)  

    # ✅ NEW COLUMNS
    aircraft = db.Column(db.String(100), nullable=True)
    flight_class = db.Column(db.String(50), nullable=True)  # Economy, Business, etc.

    def __repr__(self):
        return f"<Flight {self.flight_number}>"


# ✅ **Database Connection Function**
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="flysmart"
        )
    except mysql.connector.Error as err:
        print(f"⚠️ Database Connection Error: {err}")
        return None

# ✅ Fetch Flights with NULL Arrival Time
def fetch_flights_with_null_arrival_time():
    connection = get_db_connection()
    flights = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM flight WHERE arrival_time IS NULL")
            flights = cursor.fetchall()
        except Exception as e:
            print("Error fetching flights:", e)
        finally:
            cursor.close()
            connection.close()
    return flights


@app.route('/flights_json')
def get_flights_json():
    flights = Flight.query.all()
    flight_data = []
    for flight in flights:
        flight_data.append({
            'flight_number': flight.flight_number,
            'departure': flight.departure,
            'arrival': flight.arrival,
            'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M:%S') if flight.departure_time else None,
            'arrival_time': flight.arrival_time.strftime('%Y-%m-%d %H:%M:%S') if flight.arrival_time else None,
            'price': float(flight.price),
            'airlines': flight.airline,
            'flight_class': flight.flight_class,
            'aircraft': flight.aircraft,
            "seats_available": flight.available_seats,
        })
    return jsonify(flight_data)



# ✅ Adjust Flights Dates 
def adjust_flight_dates():
    today = datetime.now()
    flights = Flight.query.all()

    for flight in flights:
        dep_time = flight.departure_time
        arr_time = flight.arrival_time

        # If departure is before today (past)
        if dep_time < today:
            # Random days to add (1 to 15)
            days_to_add = random.randint(1, 15)
            new_dep_time = today + timedelta(days=days_to_add)

            # Maintain original duration
            duration = arr_time - dep_time
            new_arr_time = new_dep_time + duration

            # Update the fields
            flight.departure_time = new_dep_time
            flight.arrival_time = new_arr_time

    # ✅ Commit all updates at once
    db.session.commit()


# ✅ Adjust flight dates before any request
@app.before_request
def update_flight_dates_before_request():
    if not hasattr(app, 'date_updated'):
        adjust_flight_dates()
        app.date_updated = True

# 📌 Home Route
@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        try:
            if isinstance(current_user.dob, str):
                current_user.dob = datetime.strptime(current_user.dob, '%Y-%m-%d')
        except Exception:
            current_user.dob = None

    # ✅ Fetch flight data from DB
    flights = Flight.query.all()

    flight_data = []

    for flight in flights:
        # ✅ Ensure datetime conversion
        if isinstance(flight.departure_time, str):
            flight.departure_time = datetime.strptime(flight.departure_time, '%Y-%m-%d %H:%M:%S')
        if isinstance(flight.arrival_time, str):
            flight.arrival_time = datetime.strptime(flight.arrival_time, '%Y-%m-%d %H:%M:%S')

        # ✅ Now calculate duration
        duration = flight.duration
        if not duration and flight.departure_time and flight.arrival_time:
            if isinstance(flight.departure_time, datetime) and isinstance(flight.arrival_time, datetime):
                diff = flight.arrival_time - flight.departure_time
                hours, remainder = divmod(diff.total_seconds(), 3600)
                minutes = remainder // 60
                duration = f"{int(hours)}h {int(minutes)}m"

    return render_template('index.html')  # ✅ No flights initially



# Account Settings Route
@app.route('/account-settings')
@login_required
def account_settings_page():
    return render_template('account_settings.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    user = current_user

    # ✅ Convert string DOB to datetime if needed
    try:
        if isinstance(user.dob, str):
            user.dob = datetime.strptime(user.dob, '%Y-%m-%d')
    except Exception:
        user.dob = None
    
    past_bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('profile.html', user=current_user, bookings=past_bookings)

# Route to edit profile
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)  # Already in your project

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.fullname = request.form.get('fullname')
        current_user.phone = request.form.get('phone')
        current_user.email = request.form.get('email')
        current_user.dob = request.form.get('dob')
        current_user.gender = request.form.get('gender')

        # Handle password change
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password or confirm_password:
            if new_password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('edit_profile'))
            elif len(new_password) < 6:
                flash("Password must be at least 6 characters.", "warning")
                return redirect(url_for('edit_profile'))
            else:
                current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=current_user)


# Route to change password
@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    if new_password == confirm_password:
        current_user.set_password(new_password)  # ✅ Use model's method
        db.session.commit()
        flash("Password changed successfully!", "success")
    else:
        flash("Passwords do not match!", "danger")
    return redirect(url_for('account_settings_page'))


# Route to handle 2FA
@app.route('/toggle-2fa', methods=['POST'])
@login_required
def toggle_2fa():
    current_user.enable_2fa = 'enable_2fa' in request.form
    db.session.commit()
    flash("2FA settings updated!", "success")
    return redirect(url_for('account_settings_page'))

# Route to update notifications
@app.route('/update-notifications', methods=['POST'])
@login_required
def update_notifications():
    current_user.email_notifications = 'email_notifications' in request.form
    current_user.sms_notifications = 'sms_notifications' in request.form
    db.session.commit()
    flash("Notification settings updated!", "success")
    return redirect(url_for('account_settings_page'))

# Route to upload profile picture
@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part')
        return redirect(url_for('profile'))

    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('profile'))

    if file:
        # Create unique filename to avoid overwrites
        filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
        
        # Save to /static/uploads/
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Save path relative to 'static' folder
        current_user.profile_pic = f'uploads/{filename}'
        db.session.commit()

        flash('Profile picture updated!')
        return redirect(url_for('profile'))

    flash('File upload failed!')
    return redirect(url_for('profile'))

# Route to delete account
@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    flash("Your account has been deleted.", "success")
    return redirect(url_for('register')) 

# Settings Route
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)


# 📌 My Bookings Route
@app.route('/my-bookings')
@login_required
def my_bookings():
    user_id = current_user.id
    # Fetch bookings from DB based on user_id
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('my_bookings.html', bookings=bookings)


# 📌 Search Flights Route
@app.route("/search", methods=["POST"])
def search_flights():
    departure = request.form.get("departure")
    arrival = request.form.get("arrival")

    # Fetch flights matching the user's search criteria
    matching_flights = Flight.query.filter_by(
        departure=departure, 
        arrival=arrival
    ).all()

    formatted_flights = []
    for flight in matching_flights:
        # Calculate duration
        if flight.arrival_time and flight.departure_time:
            duration = flight.arrival_time - flight.departure_time
            duration_hours = int(duration.total_seconds() // 3600)
            duration_minutes = int((duration.total_seconds() % 3600) // 60)
            duration_str = f"{duration_hours}h {duration_minutes}m"
        else:
            duration_str = "N/A"

        formatted_flights.append({
             "airline": flight.airline,
             "departure": flight.departure,
             "arrival": flight.arrival,
             "departure_time": flight.departure_time,
             "arrival_time": flight.arrival_time,
             "price": float(flight.price),  # Ensure it's a float
             "seats_available": flight.available_seats,
             "flight_number": flight.flight_number,
        })

    return render_template("index.html", flights=formatted_flights, search_performed=True)


# ✅ Booking Page Route
@app.route("/booking/<int:flight_id>")
@login_required
def booking_page(flight_id):
    flight = Flight.query.get_or_404(flight_id)

    base_fare = float(flight.price)
    tax = round(base_fare * 0.12638, 2)
    total_price = round(base_fare + tax, 2)

    return render_template(
        "booking.html",
        flight=flight,
        base_fare=base_fare,
        tax=tax,
        total_price=total_price
    )

# ✅ Handle Booking Form Submission with Validation
@app.route("/booking/<int:flight_id>", methods=["POST"])
@login_required
def submit_booking(flight_id):
    full_name = request.form["full_name"]
    email = request.form["email"]
    phone = request.form["phone"]

    if not re.match(r"^[a-zA-Z\s]+$", full_name):
        flash("❌ Invalid Full Name. Only letters and spaces allowed.", "danger")
        return redirect(url_for("booking_page", flight_id=flight_id))

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        flash("❌ Invalid Email Address.", "danger")
        return redirect(url_for("booking_page", flight_id=flight_id))

    if not re.match(r"^\d{10}$", phone):
        flash("❌ Phone number must be exactly 10 digits.", "danger")
        return redirect(url_for("booking_page", flight_id=flight_id))

    flash("✅ Booking submitted successfully!", "success")
    return redirect(url_for("index"))

# 📌 Confirm Booking Route (Handles booking confirmation)
@app.route("/confirm_booking", methods=["POST"])
@login_required
def confirm_booking():
    import json
    from datetime import datetime

    # 📥 Form Inputs
    full_name = request.form["full_name"]
    email = request.form["email"]
    phone = request.form.get("phone", "")
    passport = request.form["passport"]
    seat = request.form.get("seat", "")
    meal = request.form.get("meal", "")
    notes = request.form.get("notes", "")
    flight_class = request.form.get("flight_class", "")
    flight_id = request.form["flight_id"]

    print(f"🎫 Selected Flight Class: {flight_class}")

    # ✅ Add-ons Handling (From hidden inputs)
    addon_total = float(request.form.get("addon_price", 0))
    addon_list_raw = request.form.get("addon_details", "[]")
    try:
        addon_items = json.loads(addon_list_raw)
    except:
        addon_items = []

    # 🗂️ Store selected options
    addons = {
        "meal": meal if meal else "No meal preference",  # If no meal is selected, display "No meal preference"
        "seat": seat if seat else "No seat preference",  # If no seat is selected, display "No seat preference"
        "notes": notes if notes else "No additional notes"  # If no notes, display "No additional notes"
    }
    addons_json = json.dumps(addons)

    # ✈️ Flight Info & Pricing
    flight = Flight.query.get_or_404(flight_id)
    base_fare = float(flight.price)
    tax = round(base_fare * 0.12638, 2)
    total_price = round(base_fare + tax + addon_total, 2)

    source = flight.departure
    destination = flight.arrival

    if not source or not destination:
        return "Source or destination cannot be empty", 400

    # 🧾 Booking Data
    user_id = current_user.id
    passenger_name = full_name
    booking_time = datetime.utcnow()
    booking_date = datetime.utcnow()

    new_booking = Booking(
        user_id=user_id,
        flight_id=flight_id,
        source=source,
        destination=destination,
        passenger_name=passenger_name,
        email=email,
        phone=phone,
        flight_class=flight_class,
        addons=addons_json,  # Store the JSON string
        total_price=total_price,
        booking_time=booking_time,
        booking_date=booking_date
    )

    db.session.add(new_booking)
    db.session.commit()

    # 🎟️ Ticket ID
    new_booking.ticket_id = f"FS{new_booking.booking_date.strftime('%d%m%y')}-{new_booking.id}"
    db.session.commit()

    # 📝 Log Action
    log = SystemLog(
        user_id=current_user.id,
        action=f"Booked flight {flight.flight_number} ({flight.departure} → {flight.arrival})"
    )
    db.session.add(log)
    db.session.commit()

    # 🪑 Decrease Seat Count
    if flight.available_seats > 0:
        flight.available_seats -= 1
        db.session.commit()
    else:
        flash("No available seats left.", "error")
        return redirect(url_for('index'))

    # 📤 Send Confirmation Email
    send_confirmation_email(
        recipient_email=email,
        ticket_id=new_booking.ticket_id,
        flight_number=flight.flight_number,
        total_price=total_price,
        airline=flight.airline,
        departure=flight.departure,
        arrival=flight.arrival,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        seat_preference=seat,
        meal_option=meal,
        flight_class=flight_class,
        base_fare=base_fare,
        tax=tax,
        addon_total=round(max(addon_total, 0.0), 2),
        passenger_name=passenger_name,
        addon_items=addon_items  # ✅ Now included
    )

    flash("Booking confirmed and saved successfully!", "success")
    return render_template("success.html", booking=new_booking, flight=flight, addon_data=addons)


# ✅ **Success Page Route**
@app.route("/success")
@login_required
def success():
    return render_template("success.html")

# ✅ FLIGHT SEARCH API - Cleaned & Functional
@app.route('/flights', methods=['GET'])
def get_flights():
    source = request.args.get('source')
    destination = request.args.get('destination')

    # ✅ Log Search History
    if source and destination:
        new_log = SearchLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            source=source,
            destination=destination
        )
        db.session.add(new_log)
        db.session.commit()

        if source and destination:
            flights = Flight.query.filter_by(departure=source, arrival=destination).all()
        else:
            flights = Flight.query.all()

        flights_data = []

        for flight in flights:
            try:
                departure = flight.departure_time
                arrival = flight.arrival_time

                if isinstance(departure, datetime) and isinstance(arrival, datetime):
                    duration = arrival - departure
                    duration_hours = duration.total_seconds() // 3600
                    duration_minutes = (duration.total_seconds() % 3600) // 60
                    duration_str = f"{int(duration_hours)}h {int(duration_minutes)}m"
                else:
                    duration_str = "N/A"

                flights_data.append({
                    "id": flight.id,
                    "flight_number": flight.flight_number,
                    "departure": flight.departure,
                    "arrival": flight.arrival,
                    "departure_time": departure.strftime("%Y-%m-%d %H:%M"),
                    "arrival_time": arrival.strftime("%Y-%m-%d %H:%M"),
                    "price": float(flight.price),
                    "seats_available": flight.available_seats,
                    "airline": flight.airline or "Unknown Airline",
                    "duration": duration_str, 
                    "flight_class": flight.flight_class,
                    "aircraft": flight.aircraft
                })

            except Exception as e:
                print(f"Error processing flight {flight.flight_number}: {e}")

        return jsonify({"flights": flights_data})



# 📌 Fix-duration Route 
@app.route("/fix-durations")
def fix_durations():
    try:
        flights = Flight.query.all()
        updated_count = 0

        for flight in flights:
            if flight.departure_time and flight.arrival_time:
                duration = flight.arrival_time - flight.departure_time
                duration_hours = int(duration.total_seconds() // 3600)
                duration_minutes = int((duration.total_seconds() % 3600) // 60)
                duration_str = f"{duration_hours}h {duration_minutes}m"

                print(f"Flight {flight.flight_number} → Duration: {duration_str}")

                flight.duration = duration_str
                updated_count += 1
            else:
                print(f"Flight {flight.flight_number} has missing time fields")

        db.session.commit()
        return f"✅ Updated {updated_count} flight durations successfully."
    except Exception as e:
        print("Error:", e)
        return f"❌ Error occurred: {e}"



# 📌 Voice Assistant API
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

@app.route("/run-assistant", methods=["GET", "POST"])
def run_voice_assistant():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for flight details...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            speak(f"Searching for flights from {command}")
            return jsonify({"message": f"Searching flights for: {command}"})
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand voice command"})
        except sr.RequestError:
            return jsonify({"error": "API request failed"})
        except Exception as e:
            return jsonify({"error": str(e)})

# 📌 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')

            # ✅ Role-based redirect
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    # ✅ This MUST be outside the POST block
    return render_template('login.html')

# 📌 Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # ✅ reCAPTCHA Verification
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret_key = "6Lcc7CcrAAAAALOreMMi1SJCdJz54MPVZ87a-yx8"  # <-- Your correct Secret Key

        if not recaptcha_response:
            flash("Please complete the reCAPTCHA.", "danger")
            return redirect(url_for('register'))

        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={'secret': secret_key, 'response': recaptcha_response}
        )
        result = r.json()

        if not result.get('success'):
            flash("reCAPTCHA verification failed. Please try again.", "danger")
            return redirect(url_for('register'))

        # ✅ Password Match Check
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # ✅ Existing Email Check
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))

        # ✅ Create and Save New User
        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            dob=datetime.strptime(dob, '%Y-%m-%d'),
            gender=gender,
            role="User"
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))  # Redirect back to login page

# 📌 User Dashboard
@app.route("/user_dashboard")
@login_required
def user_dashboard():
    return f"Welcome {current_user.full_name}! You are a User."


# 📌 Admin Dashboard
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return jsonify({"error": "Access Denied!"}), 403

    flights = Flight.query.all()
    bookings = Booking.query.all()
    users = User.query.all()
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(10).all()

    # ✅ Dashboard Insight Stats
    flights_count = Flight.query.count()
    users_count = User.query.count()

    try:
        bookings_count = Booking.query.count()
        revenue_total = db.session.query(db.func.sum(Booking.total_price)).scalar() or 0
    except:
        bookings_count = 0
        revenue_total = 0


    # ✅ Popular search logs (analytics)
    popular_routes = (
        db.session.query(
            SearchLog.source,
            SearchLog.destination,
            func.count().label("count")
        )
        .group_by(SearchLog.source, SearchLog.destination)
        .order_by(func.count().desc())
        .limit(10)
        .all()
    )
      
    return render_template(
        "admin_dashboard.html",
        flights=flights,
        bookings=bookings,
        users=users,
        logs=logs,
        now=datetime.now(), 
        popular_routes=popular_routes,
        flights_count=Flight.query.count(),
        users_count=User.query.count(),
        bookings_count=Booking.query.count(),
        revenue_total=db.session.query(db.func.sum(Booking.total_price)).scalar() or 0
    )

# ✅ Flight Number Generation Function
def generate_flight_number():
    airline_code = random.choice(["AI", "6E", "SG", "G8", "UK"])  # Example airlines
    number = ''.join(random.choices(string.digits, k=3))
    return f"{airline_code}{number}"
# ✅ Add a New Flight
@app.route("/admin_dashboard/add", methods=["POST"])
@login_required
def admin_add_flight():
    if current_user.role != "admin":
        return jsonify({"error": "Access Denied!"}), 403

    flight_number = request.form["flight_number"].strip()

    existing_flight = Flight.query.filter_by(flight_number=flight_number).first()
    if existing_flight:
        suggested = generate_flight_number()
        flash(f"⚠️ Flight Number '{flight_number}' already exists! Suggested: {suggested}", "danger")
        return redirect(url_for("admin_dashboard"))

    # ✅ Save new flight if flight number is unique
    flight = Flight(
        flight_number=flight_number,
        departure=request.form["departure"],
        arrival=request.form["arrival"],
        departure_time=datetime.strptime(request.form["departure_time"], "%Y-%m-%dT%H:%M"),
        arrival_time=datetime.strptime(request.form["arrival_time"], "%Y-%m-%dT%H:%M"),
        price=float(request.form["price"]),
        airline=request.form["airline"],
        flight_class=request.form["flight_class"],
        aircraft=request.form["aircraft"],
        available_seats=int(request.form["seats_available"]),
        duration=request.form["duration"]
    )
    db.session.add(flight)
    db.session.commit()

    flash("✅ Flight added successfully!", "success")
    return redirect(url_for("admin_dashboard"))



# ✅ Delete a Flight
@app.route("/admin_dashboard/delete/<int:id>")
@login_required
def admin_delete_flight(id):
    if current_user.role != "admin":
        return jsonify({"error": "Access Denied!"}), 403

    flight = Flight.query.get(id)
    if flight:
        db.session.delete(flight)
        db.session.commit()
    return redirect(url_for("admin_dashboard"))


# ✅ Promote a User to Admin
@app.route('/admin/promote/<int:user_id>')
@login_required
def promote_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash(f"{user.full_name} has been promoted to Admin.", "success")
    return redirect(url_for('admin_dashboard'))

# ✅ Demote a User
@app.route('/admin/demote/<int:user_id>')
@login_required
def demote_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    user.role = 'user'
    db.session.commit()
    flash(f"{user.full_name} has been demoted to User.", "warning")
    return redirect(url_for('admin_dashboard'))

# ✅ Delete a User
@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself.", "danger")
        return redirect(url_for('admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "danger")
    return redirect(url_for('admin_dashboard'))


# ✅ Upload Flights from CSV/XLSX
@app.route('/admin_dashboard/upload', methods=['POST'])
@login_required
def upload_flights():
    if current_user.role != 'admin':
        return jsonify({"error": "Access Denied!"}), 403

    file = request.files['flight_file']
    if not file:
        flash("No file selected.", "warning")
        return redirect(url_for('admin_dashboard'))

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            flash("Unsupported file format.", "danger")
            return redirect(url_for('admin_dashboard'))

        count = 0
        for _, row in df.iterrows():
            flight = Flight(
                flight_number=row['flight_number'],
                departure=row['departure'],
                arrival=row['arrival'],
                departure_time=pd.to_datetime(row['departure_time']),
                arrival_time=pd.to_datetime(row['arrival_time']),
                price=float(row['price']),
                airline=row['airline'],
                flight_class=row['flight_class'],
                aircraft=row['aircraft'],
                available_seats=int(row['available_seats']),
                duration=row['duration']
            )
            db.session.add(flight)
            count += 1

        db.session.commit()
        flash(f"{count} flights added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to upload: {str(e)}", "danger")

    return redirect(url_for('admin_dashboard'))


# 📌 Search Log Model
class SearchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


    user = db.relationship('User')
    
# 📌 System Log Model
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')



# 📌 Run the Flask App
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ✅ Ensure tables are created before running the app
    app.run(host='localhost', port=5000, debug=True)  # ✅ Force localhost instead of 127.0.0.1

