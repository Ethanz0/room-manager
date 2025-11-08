from common.communication.socket_client import JsonSocketClient

def test_endpoints(app, config):
    """Define test endpoints for the Flask app"""
    @app.route("/master")
    def agents():
        return {
            "master_pi_socket": f"{config.get('master_host')}:{config.get('master_port')}",
            "master_pi_socket_port": f"{config.get('master_host')}:{config.get('master_socket_port')}",
        }

    @app.route("/test")
    def hello_master():
        with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
            response = client.send_request(
                {"action": "test", "message": "Hello from Agent Pi!"}
            )
            return response