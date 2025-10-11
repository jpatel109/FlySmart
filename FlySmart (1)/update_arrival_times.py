from datetime import timedelta
from app import app, db, Flight  # assuming your app and Flight model are in app.py

def parse_duration(duration_str):
    """Converts duration like '4h 52m' to timedelta."""
    if not duration_str:
        return None

    hours = minutes = 0
    parts = duration_str.lower().replace('h', ' h').replace('m', ' m').split()

    for i, part in enumerate(parts):
        if part == 'h':
            hours = int(parts[i - 1])
        elif part == 'm':
            minutes = int(parts[i - 1])

    return timedelta(hours=hours, minutes=minutes)

def update_arrival_times():
    with app.app_context():
        flights = Flight.query.all()
        count = 0

        for flight in flights:
            if flight.arrival_time is None and flight.departure_time and flight.duration:
                delta = parse_duration(flight.duration)
                if delta:
                    flight.arrival_time = flight.departure_time + delta
                    count += 1

        db.session.commit()
        print(f"✅ Arrival times updated for {count} flights.")

if __name__ == '__main__':
    update_arrival_times()
