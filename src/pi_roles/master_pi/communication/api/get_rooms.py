from common.communication.interface import handle_socket_request_interface as interface

from common.db.repository.repository import SQLRepository


class handle_get_rooms(interface):
    """Handle getting rooms"""

    def handle(self, data, config=None):
        with SQLRepository(config.get("remote_db_host")) as repo:
            query = "SELECT room_id, room_name, status, location, ip_address, description, capacity FROM room"
            rooms = repo.fetch_all(query)

            if rooms is None:
                return {"status": "error", "message": "Failed to fetch rooms"}

            room_list = [
                {
                    "room_id": r[0],
                    "room_name": r[1],
                    "status": r[2],
                    "location": r[3],
                    "ip_address": r[4],
                    "description": r[5],
                    "capacity": r[6],
                }
                for r in rooms
            ]
            return {"status": "success", "data": room_list}
