from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_get_all_bookings(interface):
    """ Handle retrieving all bookings"""
    def handle(self, data, config=None):
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                query = """
                    SELECT booking.*, user.first_name, user.last_name, room.room_name
                    FROM booking
                    INNER JOIN user ON booking.user_id = user.user_id
                    INNER JOIN room ON booking.room_id = room.room_id
                    ORDER BY booking.start_time DESC;
                """
                results = repo.fetch_all(query)
                
                bookings = []
                for row in results:
                    booking = {
                        "booking_id": row[0],
                        "room_id": row[1],
                        "user_id": row[2],
                        "start_time": row[3].strftime('%Y-%m-%d %H:%M:%S'),
                        "end_time": row[4].strftime('%Y-%m-%d %H:%M:%S'),
                        "access_token": row[5],
                        "checked_in": row[6],
                        "created_at": row[7].strftime('%Y-%m-%d %H:%M:%S'),
                        "first_name": row[8],
                        "last_name": row[9],
                        "room_name": row[10]
                    }
                    bookings.append(booking)
                
                return {
                    "status": "success",
                    "data": bookings
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to retrieve bookings: {str(e)}"}