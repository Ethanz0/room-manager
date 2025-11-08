import socket
import json
import struct
from abc import ABC, abstractmethod
from common.logger import OfflineConsoleLogger, LogType

class AbstractSocketClient(ABC):
    """Abstract base class for a socket client."""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
    
    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sock:
            self.sock.close()
    
    @abstractmethod
    def send_request(self, message):
        """Send a request and return the response."""

class JsonSocketClient(AbstractSocketClient):
    """Concrete implementation of AbstractSocketClient for JSON messages."""
    REQUEST_LOGGER = OfflineConsoleLogger(LogType.SOCKET_REQUEST)
    RESPONSE_LOGGER = OfflineConsoleLogger(LogType.SOCKET_RESPONSE)
    
    def _receive_exactly(self, num_bytes):
        """Receive exactly num_bytes from socket."""
        chunks = []
        bytes_received = 0
        
        while bytes_received < num_bytes:
            chunk = self.sock.recv(min(num_bytes - bytes_received, 4096))
            if not chunk:
                raise ConnectionError("Socket connection broken")
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        return b''.join(chunks)
    
    def _receive_message(self):
        """Receive length-prefixed message."""
        # Receive 4 bytes containing message length
        raw_length = self._receive_exactly(4)
        message_length = struct.unpack('!I', raw_length)[0]
        
        # Get exactly that many bytes
        data = self._receive_exactly(message_length)
        return data.decode('utf-8')
    
    def _send_message(self, message):
        """Send length-prefixed message."""
        data = message.encode('utf-8')
        length = struct.pack('!I', len(data))
        self.sock.sendall(length + data)
    
    def send_request(self, message):
        # Serialize message to JSON and send
        self.REQUEST_LOGGER.log(f"Sending request {message}")
        json_data = json.dumps(message)
        self._send_message(json_data)
        
        # Receive full response with length prefix
        response_data = self._receive_message()
        self.RESPONSE_LOGGER.log(f"Received response (length: {len(response_data)} bytes): {response_data}")
        
        return json.loads(response_data)
