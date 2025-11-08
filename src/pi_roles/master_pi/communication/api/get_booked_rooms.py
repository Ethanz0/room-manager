from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_get_booked_rooms(interface):
    """ Handle retrieving booked rooms for a user """

    def handle(self, data, config=None):
        user_id = data.get("userID")

        if user_id == None:
            return {"status": "error", "error": "missing 'user_id' field"}
        
        print(f"Retrieving booked rooms for user {user_id}")

        with SQLRepository(config.get('remote_db_host')) as repo:
            query = """
            SELECT b.booking_id, b.room_id, r.room_name, r.location, b.start_time, b.end_time, b.checked_in
            FROM booking b
            JOIN room r ON b.room_id = r.room_id
            WHERE b.user_id = %s
            """
            results = repo.fetch_all(query, (user_id,))
            if results == None:
                return {"status": "success", "data": []}
            
            rooms = []
            for row in results:
                booking = {
                    "booking_id": row[0],
                    "room_id": row[1],
                    "room_name": row[2],
                    "location": row[3],
                    "booking_date": row[4].strftime("%Y-%m-%d"),
                    "start_time": row[4].strftime("%I:%M %p"),
                    "end_time": row[5].strftime("%I:%M %p"),
                    "checked_in": row[6]
                }
                rooms.append(booking)

            print("Booked rooms from DB:", rooms)

        return {
            "status": "success", 
            "data": rooms
        }