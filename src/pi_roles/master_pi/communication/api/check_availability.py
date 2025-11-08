from common.communication.interface import handle_socket_request_interface as interface

from common.db.repository.repository import SQLRepository


class handle_check_availability(interface):
    """Handle checking room availability"""

    def handle(self, data, config=None):
        try:

            room_address = data.get("ip_address")
            if room_address is None:
                return {"status": "error", "error": "missing 'ip_address' field"}

            with SQLRepository(config.get("remote_db_host")) as repo:
                # Get room_id from ip_address
                query = """
                    SELECT 
                        r.room_id,
                        EXISTS (
                            SELECT 1
                            FROM booking b
                            WHERE b.room_id = r.room_id
                            AND (
                                    (b.start_time <= NOW() AND b.end_time >= NOW())
                                OR (
                                    DATE_SUB(b.start_time, INTERVAL 15 MINUTE) <= NOW()
                                    AND b.end_time >= NOW()
                                    AND b.checked_in = 1
                                )
                            )
                        ) AS has_active_booking,
                        (
                            SELECT b2.checked_in
                            FROM booking b2
                            WHERE b2.room_id = r.room_id
                            AND (
                                    (b2.start_time <= NOW() AND b2.end_time >= NOW())
                                OR (
                                    DATE_SUB(b2.start_time, INTERVAL 15 MINUTE) <= NOW()
                                    AND b2.end_time >= NOW()
                                    AND b2.checked_in = 1
                                )
                            )
                            LIMIT 1
                        ) AS checked_in
                    FROM room r
                    WHERE r.ip_address = %s;
                """
                result = repo.fetch_one(query, (room_address,))
                if result is None:
                    return {"status": "error", "error": "room not found"}
                room_id, has_active_booking, checked_in_db = (
                    result[0],
                    result[1],
                    result[2],
                )
                availability: bool = not bool(has_active_booking)
                checked_in = bool(checked_in_db)
                return {
                    "status": "success",
                    "room_id": room_id,
                    "available": availability,
                    "checked_in": checked_in,
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
