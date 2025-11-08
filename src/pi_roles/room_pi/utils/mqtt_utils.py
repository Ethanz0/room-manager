import json
from flask_socketio import SocketIO

from common.communication.interface import (
    on_mqtt_message_callback_interface as interface,
)
from common.logger import OfflineConsoleLogger, LogType, logger_decorator


class on_mqtt_message_callback(interface):
    """Concrete implementation of MQTT message callback."""

    socketio_server: SocketIO = None
    RECEIVE_LOGGER = OfflineConsoleLogger(LogType.MQTT_RECEIVE)

    def set_socketio_server(self, socketio_server: SocketIO):
        """Set the SocketIO server instance."""
        self.socketio_server = socketio_server

    @logger_decorator(OfflineConsoleLogger(LogType.MQTT_RECEIVE), online=False)
    def __call__(self, client, userdata, message):
        """Handle incoming MQTT messages."""
        try:
            self.RECEIVE_LOGGER.log(
                f"Received message on topic {message.topic}: {message.payload.decode()}"
            )
            payload = json.loads(message.payload.decode())
            topic = message.topic

            if topic == "admin_announcements":
                # Handle admin announcements
                announcement = {
                    "title": payload.get("title"),
                    "type": payload.get("type"),
                    "message": payload.get("message"),
                }
                if announcement:
                    self.socketio_server.emit("admin_announcement", announcement)

            elif topic == "test":
                # Handle test messages
                self.RECEIVE_LOGGER.log(f"Test message received: {payload}")

        except Exception as e:
            self.RECEIVE_LOGGER.log(f"Error processing MQTT message: {e}")
