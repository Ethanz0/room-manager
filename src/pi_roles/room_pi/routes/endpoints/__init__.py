from common.utils.room_pi.room_status import RoomStatus
from common.communication.mqtt_client import JSONMQTTClient

from .status import status_endpoint
from .test import test_endpoints


def create_endpoints(app, config, status: RoomStatus = None):
    """Create endpoints for the Flask app"""
    status_endpoint(app, config, status)
    test_endpoints(app, config)
