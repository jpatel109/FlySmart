from app import app, db, Flight  # Import Flask app, database, and Flight model
from sqlalchemy.orm import sessionmaker

def convert_duration(duration_str):
    """Convert '6h 30m' to total minutes"""
    hours, minutes = 0, 0
    if 'h' in duration_str:
        hours = int(duration_str.split('h')[0].strip())
    if 'm' in duration_str:
        minutes = int(duration_str.split('m')[0].split()[-1].strip())

    return hours * 60 + minutes  # Convert total minutes

# Run inside Flask app context
with app.app_context():
    session = db.session  # Directly use Flask-SQLAlchemy session

    # Fetch all flights and update durations
    flights = session.query(Flight).all()
    for flight in flights:
        if flight.duration:  # Ensure duration is not NULL
            flight.duration_minutes = convert_duration(flight.duration)

    # Commit changes
    session.commit()
    print("✅ Successfully updated all durations!")
