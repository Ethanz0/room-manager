"""The following SQL table creation statements are used to
initialize the database schema for the application. 
And are based on the schema defined in /documentation/er_diagram.mmd."""

sql_tables = {
    "user": """
        CREATE TABLE IF NOT EXISTS user (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(50) NOT NULL,
            sub_role VARCHAR(50),
            password VARCHAR(255) NOT NULL,
            qr_code_token VARCHAR(255)
        )
    """,
    "room": """
        CREATE TABLE IF NOT EXISTS room (
            room_id INT AUTO_INCREMENT PRIMARY KEY,
            room_name VARCHAR(100) NOT NULL,
            status VARCHAR(50),
            location VARCHAR(100),
            ip_address VARCHAR(50),
            description TEXT,
            capacity INT
        )
    """,
    "booking": """
        CREATE TABLE IF NOT EXISTS booking (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            room_id INT NOT NULL,
            user_id INT NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            access_token VARCHAR(100),
            checked_in BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES room(room_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
        )
    """,
    "usage_logs": """
        CREATE TABLE IF NOT EXISTS usage_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            type VARCHAR(50),
            description TEXT
        )
    """,
}
