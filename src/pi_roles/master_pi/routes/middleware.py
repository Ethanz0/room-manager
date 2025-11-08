import json
import os
from flask import request, session, redirect, url_for
from common.logger import OnlineConsoleLogger, OfflineConsoleLogger, LogType
from common.utils.roles import return_role_by_address


def create_middleware(app, config):
    """Define middleware for the Flask app"""

    HTTP_REQUEST_LOGGER = OnlineConsoleLogger(LogType.HTTP_REQUEST) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.HTTP_REQUEST)
    HTTP_RESPONSE_LOGGER = OnlineConsoleLogger(LogType.HTTP_RESPONSE) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.HTTP_RESPONSE)
    NETWORK_ERROR_LOGGER = OnlineConsoleLogger(LogType.NETWORK_ERROR) if os.getenv("ROLE") == "master" else OfflineConsoleLogger(LogType.NETWORK_ERROR)

    agent_addresses = config.get("agents")
    room_addresses = config.get("rooms")

    # PROTECTED_WEB_ROUTES = ["dashboard", "users", "logs"]
    PUBLIC_ROUTES = ["index", "login"]

    @app.before_request
    def check_authentication():
        if request.endpoint not in PUBLIC_ROUTES:
            # Check if user is logged in
            if "user" not in session:
                return redirect(url_for("index"))
        return None

    @app.before_request
    def before_request():
        remote_addr = request.remote_addr  # Client IP address
        role = return_role_by_address(remote_addr, agent_addresses, room_addresses)
        HTTP_REQUEST_LOGGER.log(
            HTTP_REQUEST_LOGGER.log_to_db(
                f"Incoming request: {request.method} {request.path} from {remote_addr} [Role: {role}]"
            )
        )

    @app.after_request
    def pretty_print_response(response):
        try:
            if response.content_type == "application/json":
                data = json.loads(response.get_data())
                pretty = json.dumps(data, indent=2, ensure_ascii=False)
                HTTP_RESPONSE_LOGGER.log(
                    HTTP_RESPONSE_LOGGER.log_to_db(
                        f"Response to {request.method} {request.path}:\n{pretty}"
                    )
                )
        except Exception as e:
            NETWORK_ERROR_LOGGER.log(
                NETWORK_ERROR_LOGGER.log_to_db(
                    f"Error pretty-printing response for {request.method} {request.path}: {e}"
                )
            )
        return response
