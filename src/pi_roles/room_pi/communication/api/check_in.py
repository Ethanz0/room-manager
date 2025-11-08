from common.communication.interface import handle_socket_request_interface as interface
from common.communication.socket_client import JsonSocketClient

class handle_check_in(interface):
    """ Handle room check-in requests. """
    def handle(self, data, config=None):
        bookingID = data.get("bookingID")
        accessToken = data.get("accessToken")
        
        if bookingID == None:
            return {"status": "error", "error": "missing 'bookingID' field"}
        if accessToken == None:
            return {"status": "error", "error": "missing 'accessToken' field"}
        
        master_host = config.get("master_host")
        master_socket_port = config.get("master_socket_port")
        
        with JsonSocketClient(master_host, master_socket_port) as client:
            response = client.send_request({"action": "check_in_room", "bookingID": bookingID, "accessToken": accessToken})
            print("Response from socket server:", response)
            if response["status"] == "success":
                return {"status": "success", "message": "Check-in successful"}
            return {"status": "error", "error": response["error"]}
