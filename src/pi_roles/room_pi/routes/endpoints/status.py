from common.utils.room_pi.room_status import RoomStatus


def status_endpoint(app, config, status: RoomStatus = None):
    """Create status endpoint for the Flask app"""

    @app.route("/api/status")
    def api_status():
        # Return the RoomPi status dynamically
        try:
            response = status.as_dict() if status else None
            return response
        except Exception as e:
            return {"error": str(e)}
