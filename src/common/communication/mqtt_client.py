import json
from abc import ABC, abstractmethod
import threading
import os
import atexit
import paho.mqtt.client as mqtt

from common.communication.interface import (
    on_mqtt_message_callback_interface as callback_base,
)
from common.logger import OfflineConsoleLogger, LogType, logger_decorator


class MQTTClientInterface(ABC):
    """Abstract base class for MQTT clients."""

    INFO_LOGGER = OfflineConsoleLogger(LogType.MQTT_INFO)
    PUBLISH_LOGGER = OfflineConsoleLogger(LogType.MQTT_PUBLISH)
    SUBSCRIBE_LOGGER = OfflineConsoleLogger(LogType.MQTT_SUBSCRIBE)
    UNSUBSCRIBE_LOGGER = OfflineConsoleLogger(LogType.MQTT_UNSUBSCRIBE)

    def __init__(
        self,
        broker_host,
        broker_port,
        client_id: str,
        on_message_callback: callback_base,
    ):
        """Create a configured MQTT client."""

    @classmethod
    @abstractmethod
    def publish(cls, topic, message):
        """Publish a message to a topic."""

    @classmethod
    @abstractmethod
    def subscribe(cls, topic):
        """Subscribe to a topic."""

    @staticmethod
    def _on_connect(client, _userdata, _flags, reason_code, _properties):
        """Handle connection event."""
        MQTTClientInterface.INFO_LOGGER.log(
            f"Client '{client._client_id.decode()}' connected with reason code {reason_code}"
        )

    @staticmethod
    def _on_disconnect(client, _userdata, reason_code, _properties):
        """Handle disconnection event."""
        MQTTClientInterface.INFO_LOGGER.log(
            f"Client '{client._client_id.decode()}' disconnected with reason code {reason_code}"
        )

    @staticmethod
    def _on_subscribe(client, _userdata, mid, granted_qos, _properties):
        """Handle subscription event."""
        MQTTClientInterface.SUBSCRIBE_LOGGER.log(
            f"Client '{client._client_id.decode()}' subscribed: mid={mid}, granted_qos={granted_qos}"
        )

    @staticmethod
    def _on_unsubscribe(client, _userdata, mid, _properties, reason_codes):
        """Handle unsubscription event."""
        MQTTClientInterface.UNSUBSCRIBE_LOGGER.log(
            f"Client '{client._client_id.decode()}' unsubscribed: mid={mid}, reason_codes={reason_codes}"
        )

    @staticmethod
    def _on_publish(client, _userdata, mid, _properties=None):
        """Handle publish event."""
        MQTTClientInterface.PUBLISH_LOGGER.log(
            f"Client '{client._client_id.decode()}' published: mid={mid}"
        )


class JSONMQTTClient(MQTTClientInterface):
    """Singleton MQTT client that handles JSON messages and manages its own lifecycle."""

    # Loggers
    PUBLISH_LOGGER = OfflineConsoleLogger(LogType.MQTT_PUBLISH)
    SUBSCRIBE_LOGGER = OfflineConsoleLogger(LogType.MQTT_SUBSCRIBE)
    UNSUBSCRIBE_LOGGER = OfflineConsoleLogger(LogType.MQTT_UNSUBSCRIBE)
    INFO_LOGGER = OfflineConsoleLogger(LogType.MQTT_INFO)
    ERROR_LOGGER = OfflineConsoleLogger(LogType.MQTT_ERROR)

    # Singleton state
    _instance = None
    _lock = threading.Lock()

    _listening = False
    _client: mqtt.Client = None
    _topics = set()

    def __new__(
        cls,
        broker_host,
        broker_port,
        client_id: str,
        on_message_callback: callback_base,
    ):
        """Create or return singleton MQTT client instance, auto-starting listener."""
        with cls._lock:
            if not hasattr(cls, "initialized"):
                if os.environ.get("WERKZEUG_RUN_MAIN") is None or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
                    # --- Setup MQTT client ---
                    cls._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
                    cls._client.on_connect = cls._on_connect
                    cls._client.on_disconnect = cls._on_disconnect
                    cls._client.on_subscribe = cls._on_subscribe
                    cls._client.on_unsubscribe = cls._on_unsubscribe
                    cls._client.on_publish = cls._on_publish

                    if on_message_callback:
                        cls._client.on_message = on_message_callback

                    cls._client.reconnect_delay_set(min_delay=1, max_delay=5)
                    cls._client.connect(broker_host, broker_port, keepalive=30)
                    cls.INFO_LOGGER.log(
                    f"MQTT client with {client_id} connecting to {broker_host}:{broker_port}"
                    )

                    # Register cleanup for shutdown
                    atexit.register(cls._cleanup)

                    # mark as initialized so reloader/duplicate runs won't reinitialize
                    cls.initialized = True
        return cls._client

    @classmethod
    def start_listening(cls):
        """Start MQTT client loop if not already started."""
        with cls._lock:
            if getattr(cls, "_listening", False) or cls._client is None:
                return
            try:
                cls._client.reconnect()
                cls._client.loop_start()
                print(list(cls._topics))
                for topic in list(cls._topics):
                    cls.subscribe(topic)  # Resubscribe to existing topics
                cls._listening = True
                cls.INFO_LOGGER.log("MQTT listening started")
            except Exception as e:
                cls.ERROR_LOGGER.log(f"Error starting MQTT listening: {e}")

    @classmethod
    def stop_listening(cls):
        """Stop MQTT client loop."""
        with cls._lock:
            if not getattr(cls, "_listening", False) or cls._client is None:
                return
            try:
                cls._client.loop_stop()
                cls._client.disconnect()
                cls._listening = False
                cls.INFO_LOGGER.log("MQTT listening stopped")
            except Exception as e:
                cls.ERROR_LOGGER.log(f"Error stopping MQTT listening: {e}")

    @classmethod
    def _cleanup(cls):
        """Ensure clean shutdown on program exit."""
        cls.stop_listening()

    @classmethod
    def instance(cls):
        """Get the singleton instance without re-initializing."""
        if cls._client is None:
            raise RuntimeError("JSONMQTTClient has not been initialized yet.")
        return cls._client

    @classmethod
    @logger_decorator(PUBLISH_LOGGER, online=False)
    def publish(cls, topic, message: dict):
        """Publish JSON message to MQTT topic."""
        cls._client.publish(topic, json.dumps(message))

    @classmethod
    @logger_decorator(SUBSCRIBE_LOGGER, online=False)
    def subscribe(cls, topic):
        """Subscribe to MQTT topic."""
        cls._topics.add(topic)
        cls._client.subscribe(topic)

    @classmethod
    @logger_decorator(UNSUBSCRIBE_LOGGER, online=False)
    def unsubscribe(cls, topic):
        """Unsubscribe from MQTT topic."""
        cls._topics.discard(topic)
        cls._client.unsubscribe(topic)
