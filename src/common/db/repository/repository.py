import time
import os
import atexit
import threading

from abc import ABC, abstractmethod
import MySQLdb as sql
from dotenv import load_dotenv
from common.logger import OnlineConsoleLogger, OfflineConsoleLogger, logger_decorator, LogType


class DatabaseRepository(ABC):
    """Abstract base class for database repository."""

    @abstractmethod
    def _connect(self):
        """Establish a database connection."""

    @abstractmethod
    def execute_query(self, query, params=None):
        """Execute a query with optional parameters, for write (create, update, delete) operations."""

    @abstractmethod
    def fetch_all(self, query, params=None) -> list[tuple] | None:
        """Fetch all results from a query."""

    @abstractmethod
    def fetch_many(self, query, params=None, size=10) -> list[tuple] | None:
        """Fetch a limited number (size) of results from a query."""

    @abstractmethod
    def fetch_one(self, query, params=None) -> list[tuple] | None:
        """Fetch a single result from a query."""

    @abstractmethod
    def close(self):
        """Close the database connection."""


class SQLRepository(DatabaseRepository):
    """SQL database repository implementation."""

    # Resources (ideally single repository per client, hence singleton pattern)
    _instance = None
    _initialized = False
    _connection = None

    # Need to init the following:
    HOST = None
    USER = None
    PASSWORD = None
    DATABASE = None

    LOGGER_QUERY: OnlineConsoleLogger = OnlineConsoleLogger(LogType.DB_QUERY) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.DB_QUERY)
    LOGGER_ERROR: OnlineConsoleLogger = OnlineConsoleLogger(LogType.DB_ERROR) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.DB_ERROR)
    LOGGER_INFO: OnlineConsoleLogger = OnlineConsoleLogger(LogType.DB_INFO) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.DB_INFO)

    def __new__(cls, host: str):
        # Singleton pattern implementation
        if cls._instance is None:
            cls._instance = super(SQLRepository, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host: str):
        if self._initialized:
            return
        self._initialized = True
        self.HOST = host
        # Load user, password, and database for SQL server from .env file
        load_dotenv()
        self.USER = os.getenv("DB_USER")
        self.PASSWORD = os.getenv("DB_PASSWORD")
        self.DATABASE = os.getenv("DB_NAME")
        self._connect()
        atexit.register(self.close)

    def instance(self):
        """Get the singleton instance of SQLRepository"""
        if SQLRepository._instance is None:
            raise ValueError(
                "SQLRepository not initialized. Call SQLRepository(host) first."
            )
        return SQLRepository._instance

    def __enter__(self):
        return self.instance()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _connect(self):
        max_retries = 3
        retry_delay = 3  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                self._connection = sql.connect(
                    host=self.HOST,
                    user=self.USER,
                    passwd=self.PASSWORD,
                    db=self.DATABASE,
                )
                self.LOGGER_INFO.log(
                    self.LOGGER_INFO.log_to_db(
                        "Database connection established successfully."
                    )
                )
                return  # exit on success
            except Exception as e:
                print(f"Connection attempt {attempt} failed: {e}")
                if attempt >= max_retries:
                    raise ConnectionError(
                        self.LOGGER_ERROR.log_to_db(
                            f"Could not connect to the database server after {max_retries} attempts: {e}"
                        )
                    ) from e
                time.sleep(retry_delay)

    # Lock decorator for thread safety
    @staticmethod
    def locked_method(func):
        """Decorator to lock methods for thread safety."""
        def wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return wrapper

    lock = threading.Lock()

    @locked_method
    @logger_decorator(LOGGER_QUERY)
    def execute_query(self, query, params=None):
        if self._connection is None:
            raise ConnectionError("Database not connected")
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self._connection.commit()
            last_id = cursor.lastrowid

            print(f"Last inserted ID: {last_id}")
            return last_id
        except Exception as e:
            self._connection.rollback()
            self.LOGGER_ERROR.log_to_db(f"Error executing query: {e}")
        finally:
            cursor.close()

    @locked_method
    @logger_decorator(LOGGER_QUERY)
    def fetch_all(self, query, params=None):
        if self._connection is None:
            raise ConnectionError("Database not connected")
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            self.LOGGER_ERROR.log_to_db(f"Error fetching all: {e}")
            return None
        finally:
            cursor.close()

    @locked_method
    @logger_decorator(LOGGER_QUERY)
    def fetch_many(self, query, params=None, size=10):
        if self._connection is None:
            raise ConnectionError("Database not connected")
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchmany(size)
            return results
        except Exception as e:
            self.LOGGER_ERROR.log_to_db(f"Error fetching many: {e}")
            return None
        finally:
            cursor.close()

    @locked_method
    @logger_decorator(LOGGER_QUERY)
    def fetch_one(self, query, params=None):
        if self._connection is None:
            raise ConnectionError("Database not connected")
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Exception as e:
            self.LOGGER_ERROR.log_to_db(f"Error fetching one: {e}")
            return None
        finally:
            cursor.close()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
