from common.communication.mqtt_client import JSONMQTTClient

def create_middleware(app, config):
    """Create middleware for the Flask app"""

    @app.before_request
    def before_request_func():
        JSONMQTTClient.start_listening()
        return None

    @app.after_request
    def after_request_func(response):
        return response
