from abc import ABC, abstractmethod
import atexit
import os
import threading
import subprocess
import platform
from dotenv import load_dotenv

from common.db.server.init import init_db_config

class DatabaseServer(ABC):
    """Abstract base class for database server."""

    @abstractmethod
    def run(self):
        """Start the database server."""

    @abstractmethod
    def stop(self):
        """Stop the database server."""


class SQLServer(DatabaseServer):
    """SQL database server implementation."""

    # Configuration parameters
    HOST = None
    ROOT_USER = None
    ROOT_PASSWORD = None

    # Resource to manage server thread
    _stop_event = None

    def __init__(self, host: str):
        self._stop_event = threading.Event()
        self.HOST = host
        load_dotenv()
        self.ROOT_USER = os.getenv("DB_ROOT_USER")
        self.ROOT_PASSWORD = os.getenv("DB_ROOT_PASSWORD")

    def run(self):
        print(f"Starting SQL Database Server at {self.HOST}...")
        try:
            command = self._get_start_command()
            subprocess.run(command, check=True, shell=True)
            atexit.register(self.stop)  # Ensure server stops on exit
            init_db_config(self.HOST, self.ROOT_USER, self.ROOT_PASSWORD)
            print(f"SQL Database Server is running at {self.HOST} (Ctrl+C to stop)...")
            try:
                while not self._stop_event.is_set():
                    # Wait up to 1 second, then check again
                    self._stop_event.wait(timeout=1)
            except KeyboardInterrupt:
                print("Received interrupt. Stopping server...")
        except subprocess.CalledProcessError as e:
            print(f"Error starting SQL server: {e}")

    def stop(self):
        if self._stop_event.is_set():
            return  # Already stopped, do nothing
        print(f"Stopping SQL Database Server at {self.HOST}...")
        self._stop_event.set()
        try:
            command = self._get_stop_command()
            subprocess.run(command, check=True, shell=True)
            print(f"SQL Database Server at {self.HOST} stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping SQL server at {self.HOST}: {e}")

    def _get_start_command(self):
        """Return the appropriate command for the OS."""
        system = platform.system()

        if system == "Darwin":
            # macOS (example using Homebrew)
            return "brew services start mysql"
        if system == "Linux":
            # Raspberry Pi or Ubuntu
            return "sudo systemctl start mysql"
        raise NotImplementedError(f"Unsupported OS: {system}")

    def _get_stop_command(self):
        """Return the appropriate stop command for the OS."""
        system = platform.system()

        if system == "Darwin":
            return "brew services stop mysql"
        if system == "Linux":
            return "sudo systemctl stop mysql"
        raise NotImplementedError(f"Unsupported OS: {system}")
