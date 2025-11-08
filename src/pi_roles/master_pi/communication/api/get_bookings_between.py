from datetime import datetime
from common.communication.interface import handle_socket_request_interface
from common.db.repository.repository import SQLRepository


class handle_get_bookings_between(handle_socket_request_interface):
    """Handle getting bookings that overlap a given interval from the Master Pi"""

    def handle(self, data, config=None):
        """Process the request to get bookings between start and end timestamps"""
        start = data.get("start_time")
        end = data.get("end_time")
        room_ip_address = data.get("room_ip_address")
        if not start or not end:
            return {
                "status": "error",
                "message": "Missing 'start_time' or 'end_time' in request data",
            }

        # parse ISO8601 timestamps
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)

            if start_dt > end_dt:
                return {
                    "status": "error",
                    "message": "'start_time' must be <= 'end_time'",
                }
        except Exception:
            return {
                "status": "error",
                "message": "Invalid timestamp format; expected ISO8601",
            }

        try:
            with SQLRepository(config.get("remote_db_host")) as repo:
                if room_ip_address:
                    bookings = repo.fetch_all(
                        "SELECT b.booking_id, b.room_id, b.user_id, "
                        "CONCAT(u.first_name, ' ', u.last_name) AS user_full_name, u.email AS user_email, "
                        "b.start_time, b.end_time, b.access_token, b.checked_in, b.created_at "
                        "FROM booking b "
                        "JOIN room r ON b.room_id = r.room_id "
                        "JOIN `user` u ON b.user_id = u.user_id "
                        "WHERE b.start_time <= %s AND b.end_time >= %s AND r.ip_address = %s "
                        "ORDER BY b.start_time ASC, b.end_time ASC",
                        (end_dt, start_dt, room_ip_address),
                    )

                else:
                    bookings = repo.fetch_all(
                        "SELECT b.booking_id, b.room_id, b.user_id, "
                        "CONCAT(u.first_name, ' ', u.last_name) AS user_full_name, u.email AS user_email, "
                        "b.start_time, b.end_time, b.access_token, b.checked_in, b.created_at "
                        "FROM booking b "
                        "JOIN `user` u ON b.user_id = u.user_id "
                        "WHERE b.start_time <= %s AND b.end_time >= %s "
                        "ORDER BY b.start_time ASC, b.end_time ASC",
                        (end_dt, start_dt),
                    )

            # convert any datetime objects in the returned rows to ISO strings so the result is JSON-serializable
            fields = [
                "booking_id",
                "room_id",
                "user_id",
                "user_full_name",
                "user_email",
                "start_time",
                "end_time",
                "access_token",
                "checked_in",
                "created_at",
            ]

            serializable_bookings = []
            for row in bookings or ():
                row_dict = {}
                for idx, cell in enumerate(row):
                    key = fields[idx] if idx < len(fields) else f"col_{idx}"
                    if isinstance(cell, datetime):
                        row_dict[key] = cell.isoformat()
                    else:
                        row_dict[key] = cell
                serializable_bookings.append(row_dict)

            return {"status": "success", "bookings": serializable_bookings}
        except Exception as e:
            return {"status": "error", "message": str(e)}
