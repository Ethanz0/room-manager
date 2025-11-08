from common.communication.interface import handle_socket_request_interface as interface
from common.db.repository.repository import SQLRepository

class handle_get_booking_stats(interface):
    """Handle retrieving booking statistics per room over time"""
    
    def handle(self, data, config=None):
        try:
            with SQLRepository(config.get('remote_db_host')) as repo:
                # Get bookings grouped by room and date
                query = """
                    SELECT 
                        r.room_name,
                        DATE(b.start_time) as booking_date,
                        COUNT(b.booking_id) as daily_bookings
                    FROM room r
                    LEFT JOIN booking b ON r.room_id = b.room_id
                    WHERE b.start_time IS NOT NULL
                    GROUP BY r.room_id, r.room_name, DATE(b.start_time)
                    ORDER BY r.room_name, booking_date
                """
                results = repo.fetch_all(query)
                
                # Also get all rooms (even those without bookings)
                room_query = "SELECT room_name FROM room ORDER BY room_name"
                all_rooms = repo.fetch_all(room_query)
                
                # Format the statistics
                stats = []
                for row in results:
                    stats.append({
                        "room_name": row[0],
                        "date": row[1].strftime('%Y-%m-%d') if row[1] else None,
                        "count": row[2]
                    })
                
                room_list = [room[0] for room in all_rooms]
                
                return {
                    "status": "success",
                    "data": stats,
                    "rooms": room_list
                }
                
        except Exception as e:
            return {"status": "error", "message": f"Failed to retrieve booking stats: {str(e)}"}