from common.communication.mqtt_client import JSONMQTTClient

def test_endpoints(app, config):
    """Create test endpoints for the Flask app"""

    @app.route("/mqtt", methods=["GET"])
    def mqtt_test():
        message = "Hello via /mqtt endpoint on Room Pi!"
        JSONMQTTClient.publish("test", message)
        return {"status": "success", "message": message}