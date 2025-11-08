from common.communication.interface import handle_socket_request_interface as interface

from common.utils.room_pi.room_status import RoomStatus

class handle_update_status(interface):
    """ Handle updating room status """

    def handle(self, data, config=None):
        try:
            required_fields = ["status_key", "status_value"]
            for field in required_fields:
                if field not in data:
                    return {"status": "error", "error": f"missing '{field}' field"}

            status_key = data.get("status_key")
            status_value = data.get("status_value")

            if status_key is None:
                return {"status": "error", "error": "invalid 'status_key' value, should not be null"}

            # Room status should already be initialized via singleton pattern
            room_status: RoomStatus = RoomStatus.instance()

            old_status_value = room_status.get(status_key)
            room_status.update(status_key, status_value)

            # Simulate successful update
            return {"status": "success", "message": f"Room {config.get('ip_address')} status updated: {status_key}: {old_status_value} → {status_value}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}