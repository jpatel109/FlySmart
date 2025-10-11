import mysql.connector
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "flysmart"
}

# Function to fetch flights from local MySQL database
def fetch_flights_from_db(departure, destination, after_time):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT f.id, f.departure_time, f.destination, f.available_seats, f.price, f.duration, u.username AS booked_by
        FROM flights f
        LEFT JOIN bookings b ON f.id = b.flight_id
        LEFT JOIN users u ON b.user_id = u.id
        WHERE f.departure_time >= %s AND f.destination = %s AND f.available_seats > 0
        ORDER BY f.price ASC, f.duration ASC
        """
        cursor.execute(query, (after_time, destination))
        flights = cursor.fetchall()

        conn.close()
        return flights

    except mysql.connector.Error as e:
        print(f"⚠️ MySQL Error: {e}")
        return []

# Function to get the best flight options based on cost & duration
def get_best_flights(departure, destination, after_time):
    print(f"🔍 Searching for flights from {departure} to {destination} after {after_time}...")

    # Fetch flights from the database
    flights = fetch_flights_from_db(departure, destination, after_time)

    # Step 2: If no flights are found, print a message
    if not flights:
        print("⚠️ No flights found in the database.")
        return []

    # Step 3: Sort flights based on price and duration
    sorted_flights = sorted(flights, key=lambda x: (x['price'], x['duration']))

    return sorted_flights

# Example Usage
if __name__ == "__main__":
    departure = "Mumbai"
    destination = "Delhi"
    after_time = datetime.now().strftime("%H:%M")

    flights = get_best_flights(departure, destination, after_time)

    if flights:
        print("\nTop 5 Flights:")
        for flight in flights[:5]:  # Show top 5 flights
            print(f"✈️ {flight['departure_time']} → {flight['destination']} | {flight['duration']} hrs | ₹{flight['price']} | Seats: {flight['available_seats']}")
    else:
        print("❌ No flights available.")
