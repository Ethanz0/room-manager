from enum import Enum, auto

class LogType(Enum):
    """Enum for levels of logging."""

    # Specific log types
    DB_QUERY = auto()
    DB_INFO = auto()
    DB_ERROR = auto()

    NETWORK = auto()
    HTTP_REQUEST = auto()
    HTTP_RESPONSE = auto()
    NETWORK_ERROR = auto()

    MQTT_INFO = auto()
    MQTT_RECEIVE = auto()
    MQTT_PUBLISH = auto()
    MQTT_SUBSCRIBE = auto()
    MQTT_UNSUBSCRIBE = auto()
    MQTT_ERROR = auto()

    SOCKET_REQUEST = auto()
    SOCKET_RECEIVE = auto()
    SOCKET_RESPONSE = auto()
    SOCKET_ERROR = auto()
    SOCKET_INFO = auto()

    # General log levels
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()