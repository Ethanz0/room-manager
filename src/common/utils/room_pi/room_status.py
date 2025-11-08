from enum import Enum, auto
from flask_socketio import SocketIO

from common.logger import OfflineConsoleLogger, LogType
from .room_handling import StatusChangedCallback


class Status(Enum):
    """Enum for different statuses of the room."""

    AVAILABLE = auto()
    RESERVED = auto()
    IN_USE = auto()
    MAINTENANCE = auto()
    FAULT = auto()


class RoomStatus:
    """A class to manage the status of the room using the Singleton Pattern. Allows updating and retrieving status values."""

    _status: dict = {}
    _socketio: SocketIO = None
    _on_change: StatusChangedCallback = None
    _config = None

    ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)

    _singleton_instance = None  # Class-level singleton for RoomStatus

    def __new__(cls, initial_status: dict = None, app: SocketIO = None, on_change: StatusChangedCallback = None, config=None):
        if cls._singleton_instance is None:
            if initial_status is None or app is None:
                raise ValueError("RoomStatus must be initialized with initial_status and app the first time.")
            cls._singleton_instance = super(RoomStatus, cls).__new__(cls)
            cls._singleton_instance._status = initial_status
            cls._singleton_instance._socketio = app
            cls._singleton_instance._on_change = on_change() if on_change else None
            cls._config = config
        return cls._singleton_instance

    @classmethod
    def instance(cls):
        """Get the singleton instance without re-initializing."""
        if cls._singleton_instance is None:
            raise RuntimeError("RoomStatus has not been initialized yet.")
        return cls._singleton_instance

    def update(self, key, value):
        """Update the status and trigger on_change callback if value changes"""
        try:
            if key not in self._status:
                raise KeyError(f"Status key '{key}' does not exist.")
            old_value = self._status.get(key)
            self._status[key] = value
            if self._on_change:
                self._on_change(self._socketio, self._config, key, old_value, value)  # pylint: disable=E1102
        except Exception as e:
            self.ERROR_LOGGER.log(f"Error updating room status: {e}")

    def get(self, key):
        """Get the current value of a status key"""
        return self._status.get(key)

    def as_dict(self):
        """Return the entire status as a dictionary"""
        return self._status

    def __repr__(self):
        # Provide a detailed representation for debugging
        return f"<RoomStatus(status={self._status})>"

    def __str__(self):
        # Provide a user-friendly string representation
        return str(self._status)
