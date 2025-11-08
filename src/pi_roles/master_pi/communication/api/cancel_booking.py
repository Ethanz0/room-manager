from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_cancel_bookings(interface):
    """ Handle cancelling room bookings """

    def handle(self, data, config=None):
        booking_id = data.get("bookingID")

        if booking_id == None:
            return {"status": "error", "error": "missing 'booking_id' field"}
        
        print(f"Cancelling booking {booking_id}")

        with SQLRepository(config.get('remote_db_host')) as repo:
            query = "DELETE FROM booking WHERE booking_id = %s"
            repo.execute_query(query, (booking_id,))
            
            print(f"Cancelled booking {booking_id}")
        
        return {"status": "success"}