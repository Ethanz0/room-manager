import json
import socket
import struct
from typing import Dict, Callable
from abc import ABC, abstractmethod

from common.logger import AbstractLogger, OnlineConsoleLogger, OfflineConsoleLogger, LogType

class ExitRequest(Exception):
    """Custom exception to signal client exit via action "exit"."""

class ClientDisconnected(Exception):
    """Custom exception to signal client disconnection."""

class BaseRequestHandler(ABC):
    """Abstract base class for handling client requests."""

    def __init__(self, client_socket, addr):
        self.client_socket = client_socket
        self.addr = addr

    @abstractmethod
    def handle(self):
        """Handle client requests."""

class RequestHandler(BaseRequestHandler):
    """Concrete implementation of BaseRequestHandler with timeout support."""

    RECEIVE_LOGGER: AbstractLogger = None
    RESPONSE_LOGGER: AbstractLogger = None
    INFO_LOGGER: AbstractLogger = None
    ERROR_LOGGER: AbstractLogger = None

    def _receive_exactly(self, num_bytes):
        """Receive exactly num_bytes from socket."""
        chunks = []
        bytes_received = 0
        
        while bytes_received < num_bytes:
            chunk = self.client_socket.recv(min(num_bytes - bytes_received, 4096))
            if not chunk:
                raise ClientDisconnected()
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        return b''.join(chunks)

    def _receive_message(self):
        """Receive length-prefixed message."""
        # First, receive 4 bytes containing message length
        raw_length = self._receive_exactly(4)
        if not raw_length:
            raise ClientDisconnected()
        
        message_length = struct.unpack('!I', raw_length)[0]
        
        # Now receive exactly that many bytes
        data = self._receive_exactly(message_length)
        return data.decode('utf-8')

    def _send_message(self, message):
        """Send length-prefixed message."""
        data = message.encode('utf-8')
        length = struct.pack('!I', len(data))
        self.client_socket.sendall(length + data)

    def _set_loggers(self, config):
        self.RECEIVE_LOGGER = OnlineConsoleLogger(LogType.SOCKET_RECEIVE) if config.get("role") == "master" else OfflineConsoleLogger(LogType.SOCKET_RECEIVE)
        self.RESPONSE_LOGGER = OnlineConsoleLogger(LogType.SOCKET_RESPONSE) if config.get("role") == "master" else OfflineConsoleLogger(LogType.SOCKET_RESPONSE)
        self.INFO_LOGGER = OnlineConsoleLogger(LogType.SOCKET_INFO) if config.get("role") == "master" else OfflineConsoleLogger(LogType.SOCKET_INFO)
        self.ERROR_LOGGER = OnlineConsoleLogger(LogType.SOCKET_ERROR) if config.get("role") == "master" else OfflineConsoleLogger(LogType.SOCKET_ERROR)

    def handle(
        self,
        handlers: Dict[str, Callable[[...], Dict]],
        config: Dict[str, any],
    ):  # pylint: disable=arguments-differ
        # Set loggers based on config
        self._set_loggers(config)
        # Set a timeout (e.g., 10 seconds) for socket operations
        self.client_socket.settimeout(10.0)
        while True:
            try:
                data = self._receive_message()
                if not data:
                    raise ClientDisconnected()

                self.RECEIVE_LOGGER.log(
                    self.RECEIVE_LOGGER.log_to_db(
                        f"Received Raw data from {self.addr}: {data}"
                    )
                )

                request = json.loads(data)
                action = request.get("action")

                if action not in handlers:
                    response = {"error": f"Unknown action '{action}' in request."}
                else:
                    handler = handlers[action]
                    response = handler(request, config)

                response_json = json.dumps(response)
                self._send_message(response_json)
                self.RESPONSE_LOGGER.log(self.RESPONSE_LOGGER.log_to_db(response))

            except socket.timeout as e:
                print(f"Timeout waiting for data from {self.addr}.")
                timeout_response = {"error": "Request timed out."}
                self._send_message(json.dumps(timeout_response))
                self.RESPONSE_LOGGER.log(self.RESPONSE_LOGGER.log_to_db(timeout_response))
                raise ClientDisconnected() from e

            except json.JSONDecodeError:
                error_response = {"error": f"Invalid JSON: {data}"}
                self._send_message(json.dumps(error_response))
                self.RESPONSE_LOGGER.log(self.RESPONSE_LOGGER.log_to_db(error_response))

            except KeyError as e:
                error_response = {"error": str(e)}
                self._send_message(json.dumps(error_response))
                self.RESPONSE_LOGGER.log(self.RESPONSE_LOGGER.log_to_db(error_response))
                raise KeyError from e

            except (ConnectionResetError, socket.error) as e:
                print(f"Socket error with client {self.addr}: {e}")
                raise ConnectionResetError() from e

            except ExitRequest as e:
                self.INFO_LOGGER.log(self.INFO_LOGGER.log_to_db(f"Client {self.addr} requested exit."))
                break

            except ClientDisconnected as e:
                self.INFO_LOGGER.log(self.INFO_LOGGER.log_to_db(f"Client {self.addr} disconnected."))
                break