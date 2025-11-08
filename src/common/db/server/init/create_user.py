import MySQLdb as sql


def create_user(connection: sql.Connection, username: str, password: str, database: str):
    """Create a new database user with specific privileges."""
    if connection is None:
        raise ConnectionError("Database not connected")
    with connection.cursor() as cursor:
        # Execute each statement separately
        # Create user
        cursor.execute(
            "CREATE USER IF NOT EXISTS %s@'%%' IDENTIFIED BY %s",
            (username, password)
        )
        
        # Grant privileges (database name cannot be parameterized in GRANT)
        grant_query = f"GRANT ALL PRIVILEGES ON `{database}`.* TO %s@'%%'"
        cursor.execute(grant_query, (username,))
        
        # Flush privileges
        cursor.execute("FLUSH PRIVILEGES")
        
        connection.commit()
