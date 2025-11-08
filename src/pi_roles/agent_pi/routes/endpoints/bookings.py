from flask import request, session
from common.communication.socket_client import JsonSocketClient

def validate_fields(data, required_fields: list[str]) -> list[str]:
    """Returns a list of fields that are missing from the data"""
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields

def bookings_endpoints(app, config):         
    """Define booking-related endpoints for the Flask app"""
    @app.route("/rooms/available")
    def get_available_rooms():
        """Fetch available rooms from the master Pi"""

        date = request.args.get('date')
        start_time = request.args.get('startTime')
        end_time = request.args.get('endTime')

        if date == None:
            return "Missing 'date' field", 400
        if start_time == None:
            return "Missing 'startTime' field", 400
        if end_time == None:
            return "Missing 'endTime' field", 400

        print(f"Fetching available rooms for {date} from {start_time} to {end_time} from the Master Pi...")
        
        with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
            response = client.send_request({"action": "get_available_rooms", "date": date, "startTime": start_time, "endTime": end_time})
            print("Response from socket server:", response)
            rooms = response["data"]
            return rooms
        
        raise Exception("unknown error during fetching available rooms")
    
    @app.route("/bookings", methods=["POST"])
    def book_room():
        """Books a room"""

        data = request.get_json()

        missing_fields = validate_fields(data, ["roomID", "date", "startTime", "endTime"])
        if len(missing_fields) > 0:
            return "Missing fields: " + str(missing_fields), 400
        
        if "user_id" not in session:
            return "User not logged in", 401

        room_id = data["roomID"]
        user_id = session["user_id"]
        date = data["date"]
        start_time = data["startTime"]
        end_time = data["endTime"]

        print(f"Booking room {room_id} from {start_time} to {end_time} on {date} from the Master Pi...")
        
        with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
            response = client.send_request({
                "action": "book_room", 
                "roomID": room_id, 
                "userID": user_id, 
                "date": date, 
                "startTime": start_time, 
                "endTime": end_time
            })
            print("Response from socket server:", response)
            if response["status"] == "success":
                return {"bookingID": response["data"]["bookingID"], "accessToken": response["data"]["accessToken"]}, 201
            if response["status"] == "error":
                if response["error"] == "room unavailable at given time":
                    return "room unavailable at given time", 409
            
        raise Exception("unknown error during booking room")
    
    @app.route("/bookings")
    def booked_rooms():
        """Retrieves booked rooms for the user with the given user_id"""
        
        if "user_id" not in session:
            return "User not logged in", 401
        
        user_id = session["user_id"]

        print(f"Retrieving booked rooms for user {user_id} from the Master Pi...")
        
        with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
            response = client.send_request({
                "action": "get_booked_rooms", 
                "userID": user_id,
            })
            print("Response from socket server:", response)
            if response["status"] == "success":
                return response["data"], 200
            
        raise Exception("unknown error during retrieving booked rooms")
    
    @app.route("/bookings/<int:booking_id>", methods=["DELETE"])
    def cancel_booking(booking_id: int):
        """Cancels the booking with the given booking_id"""

        print(f"Cancelling booking {booking_id} from the Master Pi...")
        
        with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
            response = client.send_request({
                "action": "cancel_booking", 
                "bookingID": booking_id,
            })
            print("Response from socket server:", response)
            if response["status"] == "success":
                return "Successfully cancelled booking", 204
            
        raise Exception("unknown error during cancelling booking")
    
    @app.route("/bookings/<int:booking_id>/check-in", methods=["PATCH"])
    def check_in(booking_id: int):
        """
        Checks in to the room with the given booking_id
        """
        data = request.get_json()

        missing_fields = validate_fields(data, ["accessToken", "roomID"])
        if len(missing_fields) > 0:
            return "Missing fields: " + str(missing_fields), 400
        
        accessToken = data["accessToken"]
        roomID = data["roomID"]

        print(f"Checking in {booking_id} from the Room Pi...")
        
        rooms = config.get("rooms")
        room_host = rooms[roomID - 1]
        print(f"Connecting to room host: `{room_host}`")

        with JsonSocketClient(room_host, config.get("room_socket_port")) as client:
            response = client.send_request({
                "action": "check_in", 
                "bookingID": booking_id,
                "accessToken": accessToken
            })
            print("Response from socket server:", response)
            if response["status"] == "success":
                return "Successfully checked in", 200
            if response["status"] == "error":
                if response["error"] == "not ready for check-in":
                    return "not ready for check-in", 409
                
        raise Exception("unknown error during check-in")