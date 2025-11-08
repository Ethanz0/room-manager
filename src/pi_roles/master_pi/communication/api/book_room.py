from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository
from datetime import datetime
from pi_roles.master_pi.services.secure_token_service import SecureTokenService

class handle_book_room(interface):
    """ Handle bookings rooms """

    def __is_start_time_before_end_time(self, start_time: datetime, end_time: datetime) -> bool:
        """ Returns true if start_time is before end_time """
        return start_time < end_time

    def __date_time_to_datetime(self, date_str: str, time_str: str) -> datetime:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        t = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(d, t)
    
    def __is_room_available(self, room_id: int, start_time: datetime, end_time: datetime, config) -> bool:
        """ Returns true if the given room is available at the given time """

        query = """
        SELECT room_id FROM booking
        WHERE start_time < %s AND end_time > %s AND room_id = %s
        """
        with SQLRepository(config.get('remote_db_host')) as repo:
            results = repo.fetch_all(query, (end_time, start_time, room_id))
            if len(results) == 0:
                return True
            return False

    def handle(self, data, config=None):
        room_id = data.get("roomID")
        user_id = data.get("userID")
        date = data.get("date")
        raw_start_time = data.get("startTime")
        raw_end_time = data.get("endTime") 

        if room_id == None:
            return {"status": "error", "error": "missing 'roomID' field"}
        if user_id == None:
            return {"status": "error", "error": "missing 'userID' field"}
        if date == None:
            return {"status": "error", "error": "missing 'user' field"}
        if raw_start_time == None:
            return {"status": "error", "error": "missing 'startTime' field"}
        if raw_end_time == None:
            return {"status": "error", "error": "missing 'endTime' field"}
        
        start_time = self.__date_time_to_datetime(date, raw_start_time)
        end_time = self.__date_time_to_datetime(date, raw_end_time)

        if not self.__is_start_time_before_end_time(start_time, end_time):
            return {"status": "error", "error": "startTime must be before endTime"}

        if not self.__is_room_available(room_id, start_time, end_time, config):
            return {"status": "error", "error": "room unavailable at given time"}
        
        access_token = SecureTokenService.generate_secure_token()

        with SQLRepository(config.get('remote_db_host')) as repo:
            query = """
                INSERT INTO booking (room_id, user_id, start_time, end_time, access_token)
                VALUES (%s, %s, %s, %s, %s)
            """
            booking_id = repo.execute_query(query, (room_id, user_id, start_time, end_time, access_token))

            if booking_id == None:
                return {"status": "error", "error": "failed to create booking"}
            
            return {
                "status": "success",
                "data": {
                    "bookingID": booking_id,
                    "accessToken": access_token,
                }
            }