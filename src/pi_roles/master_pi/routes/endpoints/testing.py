from common.communication.socket_client import JsonSocketClient


def testing_endpoints(app, config: dict):
    """Define testing endpoints for the Flask app"""

    @app.route("/test")
    def test():
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request(
                {"action": "test", "message": "Hello from MasterPi"}
            )
        return {"response": response}

    @app.route("/agents")
    def agents():
        return {"agents": config["agents"]}
