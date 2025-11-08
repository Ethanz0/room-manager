import threading
import os

from flask_socketio import SocketIO
try:
    from sense_hat import SenseHat
except ImportError as e:
    print(f"Sense HAT library not found: {e}")
    SenseHat = None

from pi_roles.base_pi import BasePi
from common.communication.socket_server import SocketServer
from common.communication.mqtt_client import JSONMQTTClient
from common.utils.ip_address import get_device_address
from common.logger import OfflineConsoleLogger, LogType

from .routes.endpoints import create_endpoints
from .routes.middleware import create_middleware
from .routes.pages import create_pages
from .utils.mqtt_utils import on_mqtt_message_callback


class AgentPi(BasePi):
    """AgentPi class to create Flask app for Agent Pi role"""

    config = None
    master_host = None
    master_port = None
    master_socket_port = None
    mqtt_client = None
    sense_hat: SenseHat = None
    socketio_server: SocketIO = None

    ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)

    def create_routes(self, app, config):
        """Define routes for the Flask app"""
        # For using sessions in Flask, a secret key is required
        self.socketio_server = SocketIO(app)
        self._init_vars(self.config)
        app.secret_key = os.getenv("SECRET_KEY")
        create_middleware(app, config)
        create_pages(app, config)
        create_endpoints(app, config)

    def create_app(self, config, app_dir=__file__, app_name=__name__, debug=False):
        """Call the parent method to create routes"""
        self.config = config
        server = SocketServer(
            config.get("socket_host"),
            config.get("socket_port"),
            config=config,
            debug=debug,
        )
        socket_server_thread = threading.Thread(target=server.run, daemon=True)
        socket_server_thread.start()
        return super().create_app(config, app_dir, app_name)

    def _init_vars(self, config):
        """Initialize any additional variables if needed"""
        self.master_host = config.get("master_host")
        self.master_port = config.get("master_port")
        self.master_socket_port = config.get("master_socket_port")
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
        # create a callable callback instance and attach Sense HAT (if available)
        mqtt_callback = on_mqtt_message_callback()
        mqtt_callback.set_sense_hat(self.sense_hat)
        mqtt_callback.set_socketio_server(self.socketio_server)
        JSONMQTTClient(
            self.config.get("mqtt_broker_host"),
            self.config.get("mqtt_broker_port"),
            get_device_address(),
            mqtt_callback,  # instance is callable via its __call__
        )
        JSONMQTTClient.subscribe("room_status")
        JSONMQTTClient.subscribe("admin_announcements")
