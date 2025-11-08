import socket
import threading
import json
import os
import struct
import atexit
from typing import Dict, Callable
from abc import ABC, abstractmethod
import traceback

from common.communication.api.socket_request_handler import RequestHandler
from common.logger import (
    AbstractLogger,
    OnlineConsoleLogger,
    OfflineConsoleLogger,
    LogType,
)


class AbstractSocketServer(ABC):
    """Abstract base class for a socket server."""

    @abstractmethod
    def handle_client(self, client_socket, addr):
        """Handle a client connection."""

    @abstractmethod
    def run(self):
        """Run the server to accept connections."""


class SocketServer(AbstractSocketServer):
    """Singleton Socket Server for handling multiple clients with threading."""

    # Singleton instance and lock for thread safety
    _instance = None
    _lock = threading.Lock()

    # Data members
    _host = None
    _port = None
    _endpoints = None
    _config = None

    INFO_LOGGER: AbstractLogger = None
    ERROR_LOGGER: AbstractLogger = None

    # Singleton pattern implementation
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-checked locking
                    cls._instance = super(SocketServer, cls).__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls):
        """Get the singleton instance of the SocketServer."""
        if SocketServer._instance is None:
            raise ValueError("SocketServer not initialized yet.")
        return SocketServer._instance

    def __init__(
        self,
        host="127.0.0.1",
        port=5000,
        config=None,
        endpoints=None,
        backlog=15,
        debug=False,
    ):
        self.set_endpoints(endpoints)
        self.set_config(config)
        self._host = host
        self._port = port
        self.INFO_LOGGER = (
            OnlineConsoleLogger(LogType.SOCKET_INFO)
            if self._config.get("role") == "master"
            else OfflineConsoleLogger(LogType.SOCKET_INFO)
        )
        self.ERROR_LOGGER = (
            OnlineConsoleLogger(LogType.ERROR)
            if self._config.get("role") == "master"
            else OfflineConsoleLogger(LogType.ERROR)
        )
        # Flask hot reloading may cause 2 Socket Servers to be created, requires checks
        with self.__class__._lock:
            if (
                not hasattr(self, "initialized")
                and os.environ.get("WERKZEUG_RUN_MAIN") == "true"
                and debug
            ) or (not hasattr(self, "initialized") and not debug):
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Allow reuse of the address, to prevent "Address already in use"
                # errors caused by TIME_WAIT state after server restarts
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self._host, self._port))
                self.server_socket.listen(backlog)
                print(f"Socket Server listening on {self._host}:{self._port}")
                self.initialized = True

    def _send_message(self, message, client_socket):
        """Send length-prefixed message."""
        data = message.encode("utf-8")
        length = struct.pack("!I", len(data))
        client_socket.sendall(length + data)

    def set_endpoints(self, endpoints_dict: Dict[str, Callable[..., Dict]]):
        """Setup handlers from endpoints dictionary."""
        self._endpoints = endpoints_dict

    def set_config(self, config):
        """Set configuration for the server."""
        self._config = config

    def handle_client(self, client_socket, addr):
        # Check if INFO_LOGGER is OnlineConsoleLogger to log to DB
        if isinstance(self.INFO_LOGGER, OnlineConsoleLogger):
            self.INFO_LOGGER.log(
                self.INFO_LOGGER.log_to_db(f"New connection from {addr}")
            )
        else:
            self.INFO_LOGGER.log(f"New connection from {addr}")

        try:
            RequestHandler(client_socket, addr).handle(self._endpoints, self._config)
        except Exception as e:  # pylint: disable=broad-except
            # Safety net: catch unexpected errors
            self.ERROR_LOGGER.log(
                self.ERROR_LOGGER.log_to_db(f"Unexpected error with client {addr}: {e}")
            )
            traceback.print_exc()
            self._send_message(json.dumps({"error": "Internal server error"}), client_socket)
        finally:
            client_socket.close()

    def run(self):
        if not hasattr(self, "server_socket") or self.server_socket is None:
            self.INFO_LOGGER.log(
                "SocketServer not properly initialized or in debug mode."
            )
            return

        atexit.register(self.stop)
        # make accept interruptible by setting a timeout and handling socket closure
        self.server_socket.settimeout(1.0)
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
            except socket.timeout:
            # timeout allows us to re-check whether the socket was closed by stop()
                continue
            except OSError:
            # server_socket was closed (e.g. by stop()), exit the loop cleanly
                break
            except Exception as e:  # pylint: disable=broad-except
            # unexpected error, log and break
                if self.ERROR_LOGGER:
                    self.ERROR_LOGGER.log(
                    f"Error accepting connection: {e}"
                    )
                break

            threading.Thread(
            target=self.handle_client, args=(client_socket, addr), daemon=True
            ).start()

    def stop(self):
        """Close the socket after the server stops running."""
        if self.server_socket:
            self.server_socket.close()
            self.INFO_LOGGER.log(
                f"Socket Server stopped listening at {self._host}:{self._port}."
            )


if __name__ == "__main__":
    # Create a singleton instance for use
    server = SocketServer()
    server.run()
