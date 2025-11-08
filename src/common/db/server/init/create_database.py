import MySQLdb as sql


def create_database(connection: sql.Connection, database: str):
    """Select and create a database if it does not exist."""
    if connection is None:
        raise ConnectionError("Database not connected")
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        connection.commit()
        # Reconnect to the newly created database
        connection.select_db(database)
