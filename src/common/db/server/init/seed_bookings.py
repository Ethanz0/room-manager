from datetime import datetime, timedelta
import random
import MySQLdb as sql
from common.logger import OnlineConsoleLogger, LogType

def seed_bookings(connection: sql.Connection):
    """Seed booking data with past and future bookings for testing."""
    LOGGER = OnlineConsoleLogger(LogType.DB_INFO)
    
    if connection is None:
        raise ConnectionError("Database not connected")
    
    cursor = connection.cursor()
    
    # Check if booking table already has data
    cursor.execute("SELECT COUNT(*) FROM booking")
    count = cursor.fetchone()[0]
    
    if count > 0:
        LOGGER.log(f"Booking table already has {count} rows. Skipping seed.")
        cursor.close()
        return
    
    # Get all room IDs and user IDs
    cursor.execute("SELECT room_id FROM room")
    room_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT user_id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    if not room_ids or not user_ids:
        LOGGER.log("No rooms or users found. Please seed them first.")
        cursor.close()
        return
    
    # Generate bookings for 60 days
    today = datetime.now()
    start_date = today - timedelta(days=30)
    
    booking_data = []
    
    for room_id in room_ids:
        # Each room starts booking on a random day
        room_start = start_date + timedelta(days=random.randint(0, 20))
        

        bookings_per_day_range = (random.randint(0, 1), random.randint(2, 4))
        
        current_date = room_start
        for _ in range(40):
            # Random number of bookings per day
            num_bookings = random.randint(*bookings_per_day_range)
            
            for _ in range(num_bookings):
                user_id = random.choice(user_ids)
                start_time = current_date + timedelta(hours=random.randint(8, 16))
                end_time = start_time + timedelta(hours=random.randint(1, 3))

                booking_data.append((
                    room_id,
                    user_id,
                    start_time,
                    end_time,
                    f"abc1234",
                    current_date < today
                ))
            
            current_date += timedelta(days=1)
    
    insert_query = """
        INSERT INTO booking (room_id, user_id, start_time, end_time, access_token, checked_in)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    success_count = 0
    for booking in booking_data:
        try:
            cursor.execute(insert_query, booking)
            success_count += 1
        except Exception as e:
            LOGGER.log(f"Error seeding booking: {e}")
    
    connection.commit()
    cursor.close()
    LOGGER.log(f"Successfully seeded {success_count}/{len(booking_data)} bookings")