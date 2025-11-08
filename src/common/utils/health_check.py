import time
import MySQLdb as sql

def sql_health_check(HOST: str, USER: str, PASSWORD: str):
    """Perform a health check to ensure the SQL server is running and accessible."""
    # Health check: Wait for the server to be ready before proceeding
    max_attempts = 10
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Health check attempt {attempt}/{max_attempts}...")
            with sql.connect(
                host=HOST,
                user=USER,
                passwd=PASSWORD,
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                print("Health check successful: Connected to SQL server.")
                break  # Health check successful
        except Exception:
            print("Health check failed: Unable to connect. Retrying...")
            time.sleep(1.5)
    else:
        raise ConnectionError(
            "Health check failed: Unable to connect to SQL server after several attempts."
        )