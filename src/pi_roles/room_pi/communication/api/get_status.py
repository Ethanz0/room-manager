from common.communication.interface import handle_socket_request_interface as interface
from common.utils.room_pi.room_status import RoomStatus

class handle_get_status(interface):
    """ Handle getting room status """

    def handle(self, data, config=None):
        try:
            room_status: RoomStatus = RoomStatus.instance()
            status = room_status.as_dict()
            return {"status": "success", "data": status}
        except Exception as e:
            return {"status": "error", "error": str(e)}