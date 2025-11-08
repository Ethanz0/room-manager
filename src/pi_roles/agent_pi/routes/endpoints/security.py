from flask import session, request
from common.communication.socket_client import JsonSocketClient


def security_endpoints(app, config):
    """Define endpoints for security-related actions"""

    @app.route("/api/change-status", methods=["POST"])
    def change_status():
        try:
            user_role = session["user_role"]
            if user_role != "Security":
                return {"status": "error", "error": "Unauthorized access"}, 403

            room_ip_address = str(request.form.get("ip_address"))
            new_status_key = request.form.get("status_key")
            new_status = request.form.get("status_value")

            with JsonSocketClient(
                room_ip_address, config.get("room_socket_port")
            ) as client:
                response = client.send_request(
                    {
                        "action": "update_status",
                        "status_key": new_status_key,
                        # "" is return to default state (check for availability)
                        "status_value": None if new_status == "" else new_status,
                    }
                )
                if response.get("status") == "success" and response.get("message"):
                    return {"status": "success", "response": response.get("message")}, 200
                else:
                    return {
                        "status": "error",
                        "error": response.get("error", "Unknown error"),
                    }, 500

        except Exception as e:
            return {"status": "error", "error": str(e)}, 500
