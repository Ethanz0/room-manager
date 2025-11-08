from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class handle_check_in_room(interface):
    """ Handle checking into rooms """

    def __is_ready_for_check_in(self, start_time: datetime) -> bool:
        """Returns true if it is less than 15 minutes before start_time"""
        tz = ZoneInfo("Australia/Melbourne")
        now = datetime.now(tz=tz)
        
        # Make start_time tz-aware if it's naive
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=tz)
        
        delta = start_time - now
        return delta <= timedelta(minutes=15)

    def handle(self, data, config=None):
        booking_id = data.get("bookingID")
        accessToken = data.get("accessToken")

        if booking_id == None:
            return {"status": "error", "error": "missing 'booking_id' field"}
        if accessToken == None:
            return {"status": "error", "error": "missing 'accessToken' field"}
        
        print(f"Checking in booking {booking_id}")

        with SQLRepository(config.get('remote_db_host')) as repo:
            query = "SELECT access_token, checked_in, start_time FROM booking WHERE booking_id = %s"
            result = repo.fetch_one(query, (booking_id,))

            if result == None:
                return {"status": "error", "error": "booking ID not found"}

            if result[1] == True:
                return {"status": "error", "error": "already checked in"}
            
            if not self.__is_ready_for_check_in(result[2]):
                return {"status": "error", "error": "not ready for check-in"}
            
            if result[0] != accessToken:
                return {"status": "error", "error": "invalid access token"}
            
            query = "UPDATE booking SET checked_in = TRUE WHERE booking_id = %s"
            repo.execute_query(query, (booking_id,))

            return {"status": "success", "message": "check in successful"}
        