import mysql.connector
from mysql.connector import Error
import logging

# Configure logging for error tracking
logging.basicConfig(filename='db_error.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to establish connection with the database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",   # MySQL server (localhost)
            user="root",        # Your MySQL username
            password="123456789",  # Your MySQL password
            database="flysmart",   # Database name
            port=3306           # MySQL default port
        )
        if connection.is_connected():
            print("Connected to MySQL Database: flysmart")
        return connection
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch available flights from the database
def fetch_flights(after_time):
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT id, departure_time, destination, available_seats, price, duration
            FROM flights
            WHERE departure_time > %s
        """
        cursor.execute(query, (after_time,))
        flights = cursor.fetchall()
        return flights
    except Error as e:
        logging.error(f"Error fetching flights: {e}")
        print(f"Error fetching flights: {e}")
        return []
    finally:
        cursor.close()
        close_connection(connection)

# Function to insert a booking into the database
def insert_booking(user_id, flight_id):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        query = """INSERT INTO bookings (user_id, flight_id, booking_date) 
                   VALUES (%s, %s, NOW())"""
        cursor.execute(query, (user_id, flight_id))
        connection.commit()
        print("Booking successful!")
        return True
    except Error as e:
        logging.error(f"Error inserting booking: {e}")
        print(f"Error inserting booking: {e}")
        return False
    finally:
        cursor.close()
        close_connection(connection)

# Function to fetch user bookings from the database
def fetch_user_bookings(user_id):
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT b.id, f.departure_time, f.destination, f.price
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            WHERE b.user_id = %s
        """
        cursor.execute(query, (user_id,))
        bookings = cursor.fetchall()
        return bookings
    except Error as e:
        logging.error(f"Error fetching user bookings: {e}")
        print(f"Error fetching user bookings: {e}")
        return []
    finally:
        cursor.close()
        close_connection(connection)

# Function to check seat availability before booking
def check_seat_availability(flight_id):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        query = "SELECT available_seats FROM flights WHERE id = %s"
        cursor.execute(query, (flight_id,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            return True
        return False
    except Error as e:
        logging.error(f"Error checking seat availability: {e}")
        print(f"Error checking seat availability: {e}")
        return False
    finally:
        cursor.close()
        close_connection(connection)

# Function to update seat count after booking
def update_seat_count(flight_id):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    try:
        query = "UPDATE flights SET available_seats = available_seats - 1 WHERE id = %s AND available_seats > 0"
        cursor.execute(query, (flight_id,))
        connection.commit()
        return cursor.rowcount > 0  # Returns True if rows were updated
    except Error as e:
        logging.error(f"Error updating seat count: {e}")
        print(f"Error updating seat count: {e}")
        return False
    finally:
        cursor.close()
        close_connection(connection)

# Function to close the database connection
def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")

# Example usage
if __name__ == "__main__":
    # Fetch available flights after a specific time
    flights = fetch_flights("2025-02-12 10:00:00")
    if flights:
        for flight in flights:
            print(f"Flight ID: {flight['id']}, Departure: {flight['departure_time']}, Destination: {flight['destination']}, Price: {flight['price']}")
    else:
        print("No flights found.")

    # Insert a new booking after checking seat availability
    flight_id = 1  # Replace with actual flight ID
    user_id = 1    # Replace with actual user ID

    if check_seat_availability(flight_id):
        if insert_booking(user_id, flight_id):
            update_seat_count(flight_id)
            print("Seat count updated successfully.")
        else:
            print("Booking failed.")
    else:
        print("No available seats for this flight.")

    # Fetch user bookings
    user_bookings = fetch_user_bookings(user_id)
    if user_bookings:
        for booking in user_bookings:
            print(f"Booking ID: {booking['id']}, Flight: {booking['destination']}, Departure: {booking['departure_time']}, Price: {booking['price']}")
    else:
        print("No bookings found.")
