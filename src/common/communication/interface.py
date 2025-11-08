from abc import ABC, abstractmethod
import json

from common.logger import OfflineConsoleLogger, LogType

class on_mqtt_message_callback_interface(ABC):
    """Abstract base class for MQTT message callbacks."""

    @abstractmethod
    def __call__(self, client, userdata, message):
        """Handle incoming MQTT messages."""

class handle_socket_request_interface(ABC):
    """Abstract base class for handling socket requests."""
    LOGGER_ERROR = OfflineConsoleLogger(LogType.SOCKET_ERROR)

    def __call__(self, request: str, config: dict = None) -> dict:
        # shared logic for all handlers
        data = {}
        try:
            if isinstance(request, str):
                data = json.loads(request)
            elif isinstance(request, dict):
                data = request
            if "action" not in data:
                raise ValueError("Missing 'action' field in request")
        except (json.JSONDecodeError, TypeError) as e:
            data = {}
            self.LOGGER_ERROR.log(f"Error decoding request: {e}")

        # hand off to subclass-specific logic
        return self.handle(data, config)

    @abstractmethod
    def handle(self, data: dict, config: dict = None) -> dict:
        """Process the request data."""