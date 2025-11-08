import MySQLdb as sql

def set_timezone(connection: sql.Connection):
    """Set the database timezone to Australia/Melbourne."""
    if connection is None:
        raise ConnectionError("Database not connected")
    with connection.cursor() as cursor:
        cursor.execute("SET time_zone = 'Australia/Melbourne'")
        cursor.execute("SET GLOBAL time_zone = 'Australia/Melbourne'")
        connection.commit()