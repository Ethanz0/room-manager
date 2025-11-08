import MySQLdb as sql

from common.db.server.init.tables.tables import sql_tables
from common.logger import OnlineConsoleLogger, LogType



def create_tables(connection: sql.Connection):
    """Create necessary tables in the database."""
    LOGGER_QUERY = OnlineConsoleLogger(LogType.DB_QUERY)
    if connection is None:
        raise ConnectionError("Database not connected")

    # Iterate through the SQL table creation statements and execute them
    cursor = connection.cursor()
    for table_name, create_statement in sql_tables.items():
        LOGGER_QUERY.log(f"Creating table: {table_name}")
        cursor.execute(create_statement)
    connection.commit()
    cursor.close()
