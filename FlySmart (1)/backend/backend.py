from flask import Flask, request, jsonify
import mysql.connector
import logging
from datetime import datetime

app = Flask(__name__)

# 🔹 Configure Logging
logging.basicConfig(filename="backend_error.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 MySQL Database Configuration
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "flysmart",
}

# ✅ Function to Connect to MySQL
def connect_to_db():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as e:
        logging.error(f"Database Connection Error: {e}")
        return None

# ✅ API Route: Get Available Flights from Database
@app.route("/api/flights", methods=["GET"])
def get_flights():
    departure = request.args.get("departure")
    destination = request.args.get("destination")
    after_time = request.args.get("after", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if not departure or not destination:
        return jsonify({"error": "Departure and destination are required"}), 400

    db = connect_to_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        # Fetch flights from the database
        query = """
            SELECT id, departure_time, destination, available_seats, price, duration
            FROM flights
            WHERE departure_time > %s AND destination = %s
            ORDER BY price ASC;
        """
        cursor.execute(query, (after_time, destination))
        db_flights = cursor.fetchall()

        return jsonify({"flights": db_flights})

    except mysql.connector.Error as e:
        logging.error(f"Database Query Error: {e}")
        return jsonify({"error": "Failed to fetch flights"}), 500
    finally:
        cursor.close()
        db.close()

# ✅ API Route: Book a Flight
@app.route("/api/book", methods=["POST"])
def book_flight():
    data = request.json
    flight_id = data.get("flight_id")
    user_id = data.get("user_id")

    if not flight_id or not user_id:
        return jsonify({"error": "Flight ID and User ID are required"}), 400

    db = connect_to_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()

    try:
        # Check if seats are available
        cursor.execute("SELECT available_seats FROM flights WHERE id = %s", (flight_id,))
        flight = cursor.fetchone()

        if not flight or flight[0] == 0:
            return jsonify({"error": "No seats available for this flight"}), 400

        # Book the flight (reduce seat count)
        cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = %s", (flight_id,))
        db.commit()

        # Save booking record
        cursor.execute(
            "INSERT INTO bookings (user_id, flight_id, booking_date) VALUES (%s, %s, NOW())",
            (user_id, flight_id)
        )
        db.commit()

        return jsonify({"message": "Flight booked successfully!"})

    except mysql.connector.Error as e:
        logging.error(f"Booking Error: {e}")
        return jsonify({"error": "Booking failed"}), 500
    finally:
        cursor.close()
        db.close()

# ✅ API Route: Get User Bookings
@app.route("/api/bookings", methods=["GET"])
def get_user_bookings():
    user_id = request.args.get("user_id")
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    db = connect_to_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        query = """
            SELECT b.id, f.departure_time, f.destination, f.price
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            WHERE b.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        bookings = cursor.fetchall()

        return jsonify({"bookings": bookings})

    except mysql.connector.Error as e:
        logging.error(f"User Booking Fetch Error: {e}")
        return jsonify({"error": "Failed to retrieve bookings"}), 500
    finally:
        cursor.close()
        db.close()

# ✅ Chatbot API: Respond to User Queries
@app.route("/api/chatbot", methods=["POST"])
def chatbot_response():
    data = request.json
    user_message = data.get("message", "").lower()

    chatbot_responses = {
        "hello": "Hello! How can I assist you with your flight booking?",
        "hi": "Hi there! Need help finding a flight?",
        "book a flight": "Sure! Please provide your departure and destination locations.",
        "available flights": "To check available flights, enter your departure and destination.",
        "cancel my booking": "You can cancel your booking by going to the 'My Bookings' section.",
        "default": "I'm not sure about that. Please ask me about flights or bookings!"
    }

    response_text = chatbot_responses.get(user_message, chatbot_responses["default"])
    return jsonify({"response": response_text})

# ✅ Start Flask Server
if __name__ == "__main__":
    app.run(debug=True)
