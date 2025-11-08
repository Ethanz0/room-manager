from flask import request
from common.communication.mqtt_client import JSONMQTTClient


def publish_announcement_endpoint(app, config):
    """Registers the publish announcement endpoint."""

    @app.route("/publish_announcement", methods=["POST"])
    def publish_announcement():
        """Publish an announcement at the "admin_announcements" MQTT topic."""
        try:

            title = request.form.get("announcementTitle")
            announcement_type = request.form.get("announcementType")
            message = request.form.get("announcementMessage")

            if not title or not message:
                return "Missing title or message", 400

            app.logger.info("Publishing announcement: %s", title)

            JSONMQTTClient.publish(
                "admin_announcements",
                {"title": title, "type": announcement_type, "message": message},
            )
            return "Announcement published", 200

        except Exception as e:
            app.logger.error("Error publishing announcement: %s", str(e))
            return "Internal Server Error", 500
