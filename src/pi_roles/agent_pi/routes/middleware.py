from flask import request, session, redirect, url_for
from common.communication.mqtt_client import JSONMQTTClient


def create_middleware(app, config):
    """Define middleware for the Flask app"""

    PROTECTED_WEB_ROUTES = ["book_room_page", "booked_rooms_page"]

    @app.before_request
    def check_authentication():
        # Listen to MQTT messages for alerts if user is Security
        print("User role in session:", session.get("user_role"))  # Debugging line
        if session.get("user_role") == "Security":
            JSONMQTTClient.subscribe("room_status")
            JSONMQTTClient.start_listening()
        elif session.get("user_role") == "User":
            JSONMQTTClient.unsubscribe("room_status")
            JSONMQTTClient.start_listening()
        else:
            JSONMQTTClient.stop_listening()

        endpoint = request.endpoint or ""
        if endpoint in PROTECTED_WEB_ROUTES:
            # Check if user is logged in
            if not session.get("user_id"):
                return redirect(url_for("index"))
        return None

    @app.before_request
    def before_request():
        return None

    @app.after_request
    def after_request(response):
        return response
