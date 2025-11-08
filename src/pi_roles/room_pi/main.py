import threading
import time
from flask_socketio import SocketIO

try:
    from sense_hat import SenseHat
except ImportError as e:
    print(f"Sense HAT library not found: {e}")
    SenseHat = None

from pi_roles.base_pi import BasePi
from common.communication.socket_server import SocketServer
from common.communication.mqtt_client import JSONMQTTClient
from common.utils.room_pi.room_status import RoomStatus
from common.utils.room_pi.room_handling import status_changed
from common.utils.ip_address import get_device_address
from common.logger import OfflineConsoleLogger, LogType

from .routes.middleware import create_middleware
from .routes.pages import create_pages
from .routes.endpoints import create_endpoints
from .utils.capture_sensor_data import capture_sensor_data as get_sensor_data
from .utils.mqtt_utils import on_mqtt_message_callback


from .communication.api import socket_endpoints as endpoints


class RoomPi(BasePi):
    """RoomPi class to create Flask app for Room Pi role"""

    socket_endpoints = endpoints
    socketio_server: SocketIO = None
    mqtt_client = None
    sense_hat: SenseHat = None
    config = None
    status: RoomStatus = None

    INFO_LOGGER = OfflineConsoleLogger(LogType.INFO)
    ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)

    def create_routes(self, app, config):
        """Define routes for the Flask app"""
        # WebSocket setup
        self.socketio_server = SocketIO(app)
        self._init_vars(self.socketio_server)
        create_middleware(app, config)
        create_pages(app, config)
        create_endpoints(app, config, self.status)

    def create_app(self, config, app_dir=__file__, app_name=__name__, debug=False):
        """Call the parent method to create routes"""
        self.config = config
        server = SocketServer(
            config.get("socket_host"),
            config.get("socket_port"),
            config=config,
            debug=debug,
        )
        server.set_endpoints(self.socket_endpoints)
        socket_server_thread = threading.Thread(target=server.run, daemon=True)
        socket_server_thread.start()
        # Initialize SocketIO server
        return super().create_app(config, app_dir, app_name)

    def sensor_loop(self, sense_hat: SenseHat, delay=10.0):
        """Loop to capture sensor data at regular intervals"""
        while True:
            try:
                get_sensor_data(self.status, sense_hat, self.config, delay)
            except Exception as e:
                self.ERROR_LOGGER.log(f"Error capturing sensor data: {e}")
            time.sleep(delay)

    def _init_vars(self, socketio_server: SocketIO):
        """Initialize variables specific to RoomPi"""
        # create a callable callback instance and attach SocketIO server
        mqtt_callback = on_mqtt_message_callback()
        mqtt_callback.set_socketio_server(socketio_server)
        JSONMQTTClient(
            self.config.get("mqtt_broker_host"),
            self.config.get("mqtt_broker_port"),
            get_device_address(),
            mqtt_callback,
        )
        # JSONMQTTClient.subscribe("room_status")
        JSONMQTTClient.subscribe("admin_announcements")
        JSONMQTTClient.subscribe("test")

        self.status = RoomStatus(
            {
                "room_status": None,
                "temperature": None,
                "humidity": None,
                "pressure": None,
                "upcoming_bookings": None,
            },
            app=socketio_server,
            on_change=status_changed,
            config=self.config,
        )
        if SenseHat is not None:
            try:
                sense = SenseHat()
                _ = sense.get_temperature()  # or sense.temperature
                self.sense_hat = sense
            except Exception as e:
                self.ERROR_LOGGER.log(f"Sense HAT not detected or not working: {e}")
        else:
            self.ERROR_LOGGER.log(
                "Sense HAT library not available (Possibly RTIMU missing)"
            )
        # Start capturing sensor data
        sensor_thread = threading.Thread(
            target=self.sensor_loop, args=(self.sense_hat, 10.0), daemon=True
        )
        sensor_thread.start()
