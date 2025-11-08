import MySQLdb as sql
from common.logger import OnlineConsoleLogger, LogType
from common.utils.room_pi.room_status import Status

def seed_rooms(connection: sql.Connection, rooms: list):
    """Seed initial room data into the database."""
    LOGGER = OnlineConsoleLogger(LogType.DB_INFO)
    
    if connection is None:
        raise ConnectionError("Database not connected")
    
    cursor = connection.cursor()
    
    # Check if table already has data
    cursor.execute("SELECT COUNT(*) FROM room")
    count = cursor.fetchone()[0]
    
    if count > 0:
        LOGGER.log(f"Room table already has {count} rows. Skipping seed.")
        cursor.close()
        return
    
    # Seed Room Data
    room_templates = [
        ('Conference Room A', 'Building 1, Floor 2', 'Large conference room with projector and whiteboard', 12),
        ('Conference Room B', 'Building 1, Floor 2', 'Medium conference room with TV screen', 8),
        ('Meeting Room 101', 'Building 2, Floor 1', 'Small meeting room for team discussions', 6),
        ('Meeting Room 102', 'Building 2, Floor 1', 'Small meeting room with video conferencing', 6),
        ('Lecture Room 502', 'Building 3, Floor 5', 'Very large lecture room with projector and audio system', 50),
    ]
    
    room_data = []
    for i, room_ip in enumerate(rooms):
        # Use hardcoded room templates
        if i < len(room_templates):
            name, location, description, capacity = room_templates[i]
        else:
            # Fallback if more rooms than templates
            name = f'Meeting Room {i + 1}'
            location = f'Building {(i // 10) + 1}, Floor {(i % 10) + 1}'
            description = 'General purpose meeting room'
            capacity = 6
        
        room_data.append((
            name,
            Status.AVAILABLE.name,
            location,
            room_ip,
            description,
            capacity
        ))
    
    insert_query = """
        INSERT INTO room (room_name, status, location, ip_address, description, capacity)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    success_count = 0
    for room in room_data:
        try:
            cursor.execute(insert_query, room)
            LOGGER.log(f"Seeded room: {room[0]} at {room[2]} (IP: {room[3]})")
            success_count += 1
        except Exception as e:
            LOGGER.log(f"Error seeding room {room[0]}: {e}")
    
    connection.commit()
    cursor.close()
    LOGGER.log(f"Successfully seeded {success_count}/{len(room_data)} rooms")