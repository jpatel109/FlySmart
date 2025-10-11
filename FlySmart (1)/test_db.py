import mysql.connector

try:
    # Establish connection to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456789",
        database="flysmart"
    )
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM flights LIMIT 5")  # Fetch first 5 flights
    flights = cursor.fetchall()

    if flights:
        print("✅ Database connection successful!")
        print("Sample Data from 'flights' table:")
        for flight in flights:
            print(flight)
    else:
        print("⚠️ Database connected, but no flights found in 'flights' table.")

except mysql.connector.Error as e:
    print("❌ ERROR: Unable to connect to the database.")
    print("Details:", e)
