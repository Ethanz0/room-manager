from abc import ABC, abstractmethod
import functools
import atexit
import os
from threading import Lock

import MySQLdb as sql
from common.utils.health_check import sql_health_check

from .log_type import LogType


class AbstractLogger(ABC):
    """Abstract base class for loggers."""

    def __init__(self, level: LogType):
        self.level = level

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""


class OfflineConsoleLogger(AbstractLogger):
    """Concrete logger that logs to the console in offline mode
    (Does not log to database)."""

    def log(self, message: str) -> None:
        """Log a message at the given level."""
        print(f"[{self.level.name}] {message}")

    def log_to_db(self, message: str) -> str | None:
        """A stub for compatibility with OnlineConsoleLogger."""
        return "Not logged to DB in offline mode."


class OnlineConsoleLogger(AbstractLogger):
    """Concrete logger that logs to the console and has functionality
    to save logs to a database. Uses a singleton pattern for the database
    connection."""

    # Shared resources
    _db_connection = None

    # Object resources
    level = None
    _lock = Lock()

    def __init__(self, level: LogType):
        super().__init__(level)
        # Ensure all objects share the same DB connection (singleton)
        if OnlineConsoleLogger._db_connection is None:
            OnlineConsoleLogger.set_connection(
                os.getenv("REMOTE_DB_HOST"),
                os.getenv("DB_USER"),
                os.getenv("DB_PASSWORD"),
                os.getenv("DB_NAME"),
            )

    def log(self, message: str) -> None:
        """Log a message at the given level."""
        print(f"[{self.level.name}] {message}")

    @classmethod
    def set_connection(cls, host: str, user: str, passwd: str, db: str) -> None:
        """Set the database connection for logging to DB as a singleton."""
        sql_health_check(host, user, passwd)
        if cls._db_connection is None:
            try:
                cls._db_connection = sql.connect(
                    host=host, user=user, passwd=passwd, db=db
                )
                atexit.register(cls._db_connection.close)
            except Exception as e:
                print(f"Failed to connect to database: {e}")
                cls._db_connection = None

    def log_to_db(self, message: str) -> str | None:
        """A wrapper to save a log message to the database and return the string."""
        # Lock to ensure that only one thread writes to the DB at a time
        with self._lock:
            if self._db_connection is None:
                print("Database connection is not set. Call set_connection first.")
                return None
            query = """
            INSERT INTO usage_logs (timestamp, type, description)
            VALUES (NOW(), %s, %s)
            """
            params = (self.level.name, message)
            try:
                self._db_connection.cursor().execute(query, params)
                self._db_connection.commit()
            except Exception as e:
                temp_level = self.level
                self.level = LogType.DB_ERROR
                self.log(f"Failed to log to database: {e}")
                self.level = temp_level
            return message


def logger_decorator(log_instance: OnlineConsoleLogger, online: bool = True):
    """Decorator to log function calls and returns."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message_call = f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            message_return = None
            if online and hasattr(log_instance, "log_to_db"):
                log_instance.log(log_instance.log_to_db(message_call))
            else:
                log_instance.log(message_call)
            result = func(*args, **kwargs)
            message_return = f"{func.__name__} returned {result}"
            if online and hasattr(log_instance, "log_to_db"):
                log_instance.log(log_instance.log_to_db(message_return))
            else:
                log_instance.log(message_return)
            return result

        return wrapper

    return decorator

# Example usage
if __name__ == "__main__":
    logger = OnlineConsoleLogger(LogType.DEBUG)

    @logger_decorator(logger)
    def add(a, b):
        """Add two numbers."""
        return a + b

    add(3, 4)
