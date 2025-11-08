from flask import render_template
from common.communication.socket_client import JsonSocketClient

def home_page(app, config):
    """ Home page route for Room Pi """
    @app.route("/")
    def index():
        room_name = None
        try:
            with JsonSocketClient(
                config.get("master_host"), config.get("master_socket_port")
            ) as client:
                # Test connection to Master Pi
                response = client.send_request({"action": "get_rooms"})
                if response.get("status") == "success":
                    rooms = response.get("data")
                    room_ip = config.get("ip_address")
                    for room in rooms:
                        if room.get("ip_address") == room_ip:
                            room_name = room.get("room_name")
        except Exception as e:
            app.logger.error(f"Error connecting to Master Pi: {e}")
        return render_template("home.html", role="Room", room_name=room_name, config=config)
