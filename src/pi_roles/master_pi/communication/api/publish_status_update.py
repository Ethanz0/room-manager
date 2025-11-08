import os
from common.communication.interface import handle_socket_request_interface as interface
from common.communication.mqtt_client import JSONMQTTClient
from common.logger import OnlineConsoleLogger, OfflineConsoleLogger, LogType


class handle_publish_status_update(interface):
    """Handle status update requests"""


    PUBLISH_LOGGER = OnlineConsoleLogger(LogType.MQTT_PUBLISH) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.MQTT_PUBLISH)

    def handle(self, data, config):
        """Process the status update request"""
        try:
            # extract expected fields
            topic = "room_status"
            from_addr = data.get("from_ip_address")
            status_key = data.get("status_key")
            if not status_key:
                return {"error": "Missing 'status_key' field"}
            status_old_value = data.get("status_old_value")
            status_value = data.get("status_value")
            message = data.get("message")
            if not message:
                return {"error": "Missing 'message' field"}

            message_payload = {
                "from": from_addr,
                "status_key": status_key,
                "status_old_value": status_old_value,
                "status_value": status_value,
                "message": message,
            }

            JSONMQTTClient.publish(topic, message_payload)
            self.PUBLISH_LOGGER.log(
                self.PUBLISH_LOGGER.log_to_db(
                    f"Publishing status update to topic {topic}: {message_payload}"
                )
            )

            return {
                "status": "success",
                "topic": topic,
                "data_published": message_payload,
            }

        except Exception as e:
            return {"error": str(e)}
