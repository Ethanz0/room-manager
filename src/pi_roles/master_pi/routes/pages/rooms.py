from flask import render_template, session
from common.communication.socket_client import JsonSocketClient

def rooms_pages(app, config):
    """Define routes for rooms pages"""

    @app.route("/rooms")
    def manage_rooms_page():
        """Render the view rooms page if the user is logged in, otherwise redirect to login"""
        try:
            user_role = session["user_role"]
            if user_role != "Admin":
                return "Unauthorized access", 403

            with JsonSocketClient(
                config.get("master_host"), config.get("master_socket_port")
            ) as client:
                response = client.send_request({"action": "get_rooms"})
                if response.get("status") != "success":
                    raise ValueError("Error fetching rooms")
                if response.get("data") is None:
                    raise ValueError("No rooms data received")
                rooms = response.get("data", [])
                for room in rooms:
                    try:    
                        with JsonSocketClient(room.get("ip_address"), config.get("room_socket_port")) as room_client:
                            status_response = room_client.send_request({"action": "get_status"})
                            if status_response.get("status") == "success":
                                room["status"] = status_response.get("data", {}).get("room_status")
                            else:
                                room["status"] = None
                    except Exception as e:
                        room["status"] = "N/A\nError: Unable to reach room\n" + str(e)
            return render_template("rooms.html", role="Master", rooms=rooms, config=config)
        except Exception as e:
            return f"Error fetching rooms: {e}", 500