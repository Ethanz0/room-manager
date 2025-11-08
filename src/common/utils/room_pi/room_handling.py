from abc import ABC, abstractmethod
from flask_socketio import SocketIO
from common.logger import OfflineConsoleLogger, LogType
from common.communication.socket_client import JsonSocketClient

INFO_LOGGER = OfflineConsoleLogger(LogType.INFO)
SOCKET_LOGGER = OfflineConsoleLogger(LogType.SOCKET_INFO)
ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)

class StatusChangedCallback(ABC):
    """Abstract base class for a callback function to a status change"""

    def __call__(self, socketio_server: SocketIO, config: dict, key: str, old, new):
        self.status_changed(socketio_server, config, key, old, new)

    @abstractmethod
    def status_changed(self, socketio_server: SocketIO, config: dict,  key: str, old, new):
        """Callback function when status changes"""


class status_changed(StatusChangedCallback):
    """Concrete implementation of StatusChangedCallback"""

    def status_changed(self, socketio_server: SocketIO, config: dict, key: str, old, new):
        """Callback function when status changes"""
        try:
            INFO_LOGGER.log(f"Status changed: {key} from '{old}' → '{new}'")
            notify_clients(socketio_server, {key: new})
        except Exception as e:
            ERROR_LOGGER.log(f"Error notifying clients: {e}")
        # If the room status changed, notify the master server
        if key == "room_status":
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
                        # Build a descriptive request payload for the master to record/publish the status change
                        request_payload = {
                        "from_ip_address": config.get("ip_address"),
                        "action": "publish_status_update",
                        "status_key": key,
                        "status_old_value": old,
                        "status_value": new,
                        "message": f"Status '{key}' changed from '{old}' to '{new}' by '{config.get('ip_address')}'",
                        }
                        SOCKET_LOGGER.log(f"Attempt {attempt}: Sending status update to master: {request_payload}")
                        response = client.send_request(request_payload)
                        SOCKET_LOGGER.log(f"Status update sent to master successfully: {response}")
                    break
                except Exception as e:
                    SOCKET_LOGGER.log(f"Attempt {attempt} failed sending status update to master: {e}")
                    if attempt == max_attempts:
                        ERROR_LOGGER.log("All retry attempts failed; giving up.")

def notify_clients(socketio_server: SocketIO, status: dict):
    """Notify connected clients about status updates"""
    INFO_LOGGER.log(f"Emitting status update to clients: {status}")
    socketio_server.emit('status_update', status)
