import threading
import os

from pi_roles.base_pi import BasePi
from common.communication.socket_server import SocketServer
from common.communication.mqtt_client import JSONMQTTClient
from common.utils.ip_address import get_device_address

from .communication.api import socket_endpoints as endpoints
from .routes.endpoints import create_endpoints
from .routes.middleware import create_middleware
from .routes.pages import create_pages


class MasterPi(BasePi):
    """MasterPi class to create Flask app for Master Pi role"""

    socket_endpoints = endpoints
    socket_client = None
    config = None
    mqtt_client = None

    def create_routes(self, app, config):
        """Define routes for the Flask app"""
        secret_key = os.getenv("SECRET_KEY")
        app.secret_key = secret_key
        create_middleware(app, config)
        create_pages(app, config)
        create_endpoints(app, config)

    def create_app(self, config, app_dir=__file__, app_name=__name__, debug=False):
        """Call the parent method to create routes"""
        self.config = config
        socket_server = SocketServer(
            config.get("socket_host"),
            config.get("socket_port"),
            config=config,
            debug=debug,
        )
        self._init_vars(config)
        socket_server.set_endpoints(self.socket_endpoints)
        threading.Thread(target=socket_server.run, daemon=True).start()

        return super().create_app(config, app_dir, app_name)

    def _init_vars(self, config):
        """Initialize any additional variables if needed"""
        self.mqtt_client = JSONMQTTClient(
            config.get("mqtt_broker_host"),
            config.get("mqtt_broker_port"),
            get_device_address(),
            None,
        )
