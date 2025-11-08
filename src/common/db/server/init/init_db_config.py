import os
import MySQLdb as sql
from common.utils.health_check import sql_health_check
from common.db.server.init import create_database, create_tables, create_user
from common.db.server.init.seed_users import seed_users
from common.db.server.init.seed_rooms import seed_rooms
from common.db.server.init.set_timezone import set_timezone
from common.db.server.init.seed_bookings import seed_bookings

def init_db_config(config: dict):
    """Initialize one-time database configurations."""
    host = config.get("remote_db_host")
    root_user = os.getenv("DB_ROOT_USER")
    root_password = os.getenv("DB_ROOT_PASSWORD")
    
    print(f"SQL health check using host: {host}")
    print(f"Root user: {root_user}")
    
    sql_health_check(host, root_user, root_password)
    
    with sql.connect(
        host=host,
        user=root_user,
        passwd=root_password,
    ) as connection:
        create_database(connection, os.getenv("DB_NAME"))
        create_user(
            connection,
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_NAME"),
        )
        set_timezone(connection)
        create_tables(connection)
        seed_users(connection)
        seed_rooms(connection, config.get('rooms'))

        """ Enable to demonstrate booking graph """
        # seed_bookings(connection)