import time
import threading
import json
from flask_socketio import SocketIO

try:
    from sense_hat import SenseHat
except ImportError as e:
    print(f"Sense HAT library not found: {e}")
    SenseHat = None

from common.communication.interface import (
    on_mqtt_message_callback_interface as interface,
)
from common.logger import OfflineConsoleLogger, LogType, logger_decorator


class on_mqtt_message_callback(interface):
    """Concrete implementation of MQTT message callback."""

    sense_hat: SenseHat = None
    socketio_server: SocketIO = None

    ERROR_LOGGER = OfflineConsoleLogger(LogType.MQTT_ERROR)
    RECEIVE_LOGGER = OfflineConsoleLogger(LogType.MQTT_RECEIVE)

    def set_sense_hat(self, sense_hat: SenseHat):
        """Set the Sense HAT instance."""
        self.sense_hat = sense_hat
    
    def set_socketio_server(self, socketio_server: SocketIO):
        """Set the SocketIO server instance."""
        self.socketio_server = socketio_server

    @logger_decorator(OfflineConsoleLogger(LogType.MQTT_RECEIVE), online=False)
    def __call__(self, client, userdata, message):
        """Handle incoming MQTT messages."""
        try:
                
            self.RECEIVE_LOGGER.log(f"Received message on topic {message.topic}: {message.payload.decode()}")
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

            if payload.get("status_key") == "room_status" and payload.get("status_value") == "FAULT" and payload.get("status_old_value") != "FAULT":
                # start a daemon thread to flash the Sense HAT LEDs three times
                threading.Thread(target=self._flash_three_times, args=(self.sense_hat,), daemon=True).start()
        except Exception as e:
            self.ERROR_LOGGER.log(f"Error in MQTT message callback: {e}")

    def flash_leds(self, sense_hat=None, color=(255, 0, 0), duration=0.3):
        """Flash the Sense HAT LEDs with the specified color for a duration."""
        ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)

        if sense_hat is None:
            sense_hat = self.sense_hat
        if sense_hat is None:
            ERROR_LOGGER.log("No Sense HAT available to flash LEDs.")
            return
        try:
            sense_hat.clear(color)
            time.sleep(duration)
            sense_hat.clear()
        except Exception as e:
            ERROR_LOGGER.log(f"Error flashing LEDs: {e}")

    def _flash_three_times(self, sense_hat=None):
        try:
            if sense_hat is None:
                sense_hat = self.sense_hat
            for _ in range(3):
                self.flash_leds(sense_hat)
        except Exception as e:
            OfflineConsoleLogger(LogType.ERROR).log(f"Flash thread error: {e}")