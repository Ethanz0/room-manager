from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository
from datetime import date, time, datetime

class handle_get_available_rooms(interface):
    """ Handle finding available rooms for the given date and time """

    def __get_available_rooms(self, start_time: datetime, end_time: datetime, config=None):
        """ Queries the database rooms available for the given start and end times"""
        
        with SQLRepository(config.get('remote_db_host')) as repo:
            query = """
            SELECT * FROM room WHERE room_id NOT IN (
                SELECT room_id FROM booking
                WHERE start_time < %s AND end_time > %s
            )
            """
            results = repo.fetch_all(query, (end_time, start_time))
            if results == None:
                return []
            
            rooms = []
            for row in results:
                room = {
                    "id": row[0],
                    "room_name": row[1],
                    "status": row[2],
                    "location": row[3],
                    "ip_address": row[4],
                    "description": row[5],
                    "capacity": row[6]
                }
                rooms.append(room)

            return rooms

    def __date_time_to_datetime(self, date_str: str, time_str: str) -> datetime:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        t = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(d, t)

    def handle(self, data, config=None):
        date = data.get("date")
        raw_start_time = data.get("startTime")
        raw_end_time = data.get("endTime")

        if date == None:
            return {"status": "error", "error": "missing 'user' field"}
        if raw_start_time == None:
            return {"status": "error", "error": "missing 'startTime' field"}
        if raw_end_time == None:
            return {"status": "error", "error": "missing 'endTime' field"}
        
        print(f"Querying available rooms for {date} from {raw_start_time} to {raw_end_time}")

        start_time = self.__date_time_to_datetime(date, raw_start_time)
        end_time = self.__date_time_to_datetime(date, raw_end_time)

        rooms = self.__get_available_rooms(start_time, end_time, config)
        print("Available rooms from DB:", rooms)

        return {
            "status": "success", 
            "data": rooms
        }