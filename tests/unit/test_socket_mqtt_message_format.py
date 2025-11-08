import threading
import time
import json

from unittest.mock import MagicMock, patch
from common.communication.socket_server import SocketServer
from common.communication.socket_client import JsonSocketClient
from common.communication.mqtt_client import JSONMQTTClient


def test_socket_server_returns_json_response(capfd):
    """Test that the socket server returns a JSON response."""
    # Mock the handler callback function used by the server
    mock_handle = MagicMock(return_value={"status": "success"})
    endpoints = {"test_action": mock_handle}
    port = 5001

    socket_server = SocketServer(endpoints=endpoints, port=port, config={})
    socket_server.initialized = False

    # Run server in a separate thread silently (no logs)
    thread = threading.Thread(target=socket_server.run, daemon=True)
    thread.start()

    time.sleep(2)  # Ensure the server is ready

    # Create a client and send a request
    with JsonSocketClient("localhost", port) as client:
        response = client.send_request({"action": "test_action"})
        assert response == {"status": "success"}

    mock_handle.assert_called_once()
    socket_server.stop()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("Server did not shut down")
    # Silence server output
    capfd.readouterr()


def test_mqtt_client_publish_json():
    """Test that the MQTT client publishes JSON messages correctly."""
    # Patch the MQTT Client inside JSONMQTTClient
    with patch("common.communication.mqtt_client.mqtt.Client") as MockMQTT:
        mock_client_instance = MagicMock()
        MockMQTT.return_value = mock_client_instance

        # Initialize JSONMQTTClient singleton
        client = JSONMQTTClient("localhost", 1883, "test_client", None)

        # Call publish
        message = {"status": "success"}
        JSONMQTTClient.publish("test/topic", message)

        # Check that publish was called with correct JSON string
        mock_client_instance.publish.assert_called_once()
        topic, payload = mock_client_instance.publish.call_args[0]
        assert topic == "test/topic"
        assert json.loads(payload) == {"status": "success"}

def test_mqtt_client_subscribe():
    """Test that the MQTT client subscribes to topics correctly."""
    # Reset singleton state before test
    JSONMQTTClient._client = None
    JSONMQTTClient._topics = set()
    JSONMQTTClient._listening = False
    if hasattr(JSONMQTTClient, "initialized"):
        delattr(JSONMQTTClient, "initialized")

    # Patch mqtt.Client so no real connection is attempted
    with patch("common.communication.mqtt_client.mqtt.Client") as MockMQTT:
        mock_client_instance = MagicMock()
        MockMQTT.return_value = mock_client_instance

        # Initialize the singleton
        client = JSONMQTTClient("localhost", 1883, "test_client_sub", None)

        # Call subscribe
        topic = "test/topic"
        JSONMQTTClient.subscribe(topic)

        # Assert subscribe was called on the mock client
        mock_client_instance.subscribe.assert_called_once_with(topic)

        # Assert topic added to internal _topics set
        assert topic in JSONMQTTClient._topics
