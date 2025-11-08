import threading
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from common.communication.socket_client import JsonSocketClient
from common.utils.room_pi.room_status import Status
from common.logger import OfflineConsoleLogger, LogType


def capture_sensor_data(status, sense_hat, config, delay=10.0):
    """Capture sensor data periodically and schedule the next capture."""
    INFO_LOGGER = OfflineConsoleLogger(LogType.INFO)
    ERROR_LOGGER = OfflineConsoleLogger(LogType.ERROR)
    try:
        capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        INFO_LOGGER.log(f"Capturing sensor data at {capture_time}...")

        if status:
            # Use real Sense HAT data if available
            response = get_availability(config)
            availability = response.get("available")
            checked_in = response.get("checked_in")
            if availability is None:
                raise ValueError("Failed to get room availability status")
            availability_status = None
            # Check for room status availability only if current status is AVAILABLE or IN_USE
            if (
                status.get("room_status") == Status.IN_USE.name
                or status.get("room_status") == Status.AVAILABLE.name
                or status.get("room_status") == Status.RESERVED.name
                or status.get("room_status") is None
            ):
                if not availability and checked_in:
                    availability_status = Status.IN_USE
                elif not availability and not checked_in:
                    availability_status = Status.RESERVED
                elif availability and not checked_in:
                    availability_status = Status.AVAILABLE
                else:
                    availability_status = None
            else:
                # Maintain current status, expected to be MAINTENANCE or FAULT set by admin or security
                room_status_key = status.get("room_status")
                if room_status_key in Status.__members__:
                    availability_status = Status[room_status_key]
                else:
                    availability_status = None

            # Get upcoming bookings for today
            # Use Australia/Melbourne timezone for start/end of day
            tz = ZoneInfo("Australia/Melbourne")
            now_tz = datetime.now(tz)
            start_of_day = now_tz.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now_tz.replace(hour=23, minute=59, second=59, microsecond=999999)
            bookings = get_bookings_between(
                config, start_of_day, end_of_day
            )

            if sense_hat:
                status.update("temperature", sense_hat.get_temperature())
                status.update("humidity", sense_hat.get_humidity())
                status.update("pressure", sense_hat.get_pressure())
                status.update("room_status", availability_status.name if availability_status else None)
                status.update("upcoming_bookings", bookings)
            else:
                # Simulated data if Sense HAT not available
                status.update("temperature", random.uniform(20.0, 25.0))
                status.update("humidity", random.uniform(30.0, 50.0))
                status.update("pressure", random.uniform(1000.0, 1020.0))
                status.update("room_status", availability_status.name if availability_status else None)
                status.update("upcoming_bookings", bookings)

    except Exception as e:
        ERROR_LOGGER.log(f"Error capturing sensor data: {e}")


def get_availability(config: dict):
    """Check room availability from MasterPi"""
    with JsonSocketClient(
        config.get("master_host"), config.get("master_socket_port")
    ) as client:
        room_ip = config.get("ip_address")
        response = client.send_request(
            {"action": "check_availability", "ip_address": room_ip}
        )
        if response.get("status") == "success":
            return response
        raise ValueError(
            "Failed to get room availability, did not receive success status"
        )

def get_bookings_between(config: dict, start_time: datetime, end_time: datetime):
    """Get room bookings from MasterPi using the same request shape HandleGetBookingsBetween expects."""
    with JsonSocketClient(
        config.get("master_host"), config.get("master_socket_port")
    ) as client:
        room_ip = config.get("ip_address")

        # Use an ISO8601 representation compatible with datetime.fromisoformat used by the handler.
        payload = {
            "action": "get_bookings_between",
            "room_ip_address": room_ip,
            "start_time": start_time.isoformat(sep=" ", timespec="seconds"),
            "end_time": end_time.isoformat(sep=" ", timespec="seconds"),
        }

        response = client.send_request(payload)

        # Normalized error handling to surface server-side messages
        if response.get("status") == "success":
            return response.get("bookings")
        if response.get("status") == "error":
            raise ValueError(response.get("message", "MasterPi returned an error"))
        raise ValueError("Failed to get room bookings: unexpected response from MasterPi")