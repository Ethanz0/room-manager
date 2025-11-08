import MySQLdb as sql
from common.logger import OnlineConsoleLogger, LogType

def seed_users(connection: sql.Connection):
    """Seed initial user data into the database."""
    LOGGER = OnlineConsoleLogger(LogType.DB_INFO)
    
    if connection is None:
        raise ConnectionError("Database not connected")
    
    cursor = connection.cursor()
    
    users = [
        ('Mark', 'Otto', 'mark@example.com', 'Admin', '', 'password123', None),
        ('Jacob', 'Thornton', 'jacob@example.com', 'User', 'Student', 'password123', None),
        ('Ethan', 'Zhang', 'ethan@mail.com', 'User', 'Teacher', 'password123', None),
        ('John', 'Smith', 'admin@mail.com', 'Admin', '', 'admin', None),
        ('Securimo', 'Johnson', 'security@mail.com', 'Security', '', 'security', None),
        ('Sarah', 'Connor', 'sarah@example.com', 'Admin', '', 'password123', None),
        ('John', 'Doe', 'john@example.com', 'Security', '', 'password123', None),
    ]
    # Check if user table already has data
    cursor.execute("SELECT COUNT(*) FROM user")
    count = cursor.fetchone()[0]
    
    if count > 0:
        LOGGER.log(f"User table already has {count} rows. Skipping seed.")
        cursor.close()
        return
    
    insert_query = """
        INSERT INTO user (first_name, last_name, email, role, sub_role, password, qr_code_token)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE first_name=first_name
    """
    
    for user in users:
        try:
            cursor.execute(insert_query, user)
            LOGGER.log(f"Seeded user: {user[2]}")
        except Exception as e:
            LOGGER.log(f"Error seeding user {user[2]}: {e}")
    
    connection.commit()
    cursor.close()
    LOGGER.log(f"Successfully seeded {len(users)} users")
