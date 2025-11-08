import socket
from common.logger import OfflineConsoleLogger, LogType

def get_device_address():
    """Retrieve the device's IP address."""
    INFO_LOGGER = OfflineConsoleLogger(LogType.INFO)
    # Gets the hostname
    hostname = socket.gethostname()
    INFO_LOGGER.log(f"Hostname: {hostname}")
    # Gets the IP address associated with the hostname
    ip_address = socket.gethostbyname(hostname)
    INFO_LOGGER.log(f"IP Address: {ip_address}")
    return ip_address