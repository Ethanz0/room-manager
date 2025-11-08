from flask import request, jsonify, session
from common.communication.socket_client import JsonSocketClient

def validate_fields(data, required_fields: list[str]) -> list[str]:
    """Returns a list of fields that are missing from the data"""
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields

def register_endpoints(app, config):
    """Define the registration endpoint."""

    @app.route("/registration", methods=["POST"])
    def register_user():
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid JSON data"}), 400

        missing_fields = validate_fields(data, ["firstname", "lastname", "role", "email", "password"])
        if len(missing_fields) > 0:
            return jsonify({"message": "Missing fields: " + str(missing_fields)}), 400

        first_name = data["firstname"]
        last_name = data["lastname"]
        role = data["role"]
        email = data["email"]
        password = data["password"]

        print(f"Registering user {email} through the Master Pi...")

        try:
            with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
                response = client.send_request({
                    "action": "register_user",
                    "firstName": first_name,
                    "lastName": last_name,
                    "role": role,
                    "email": email,
                    "password": password
                })
                print("Response from socket server:", response)
                
                if response["status"] == "success":
                    session["user_email"] = email
                    session["user_id"] = response["data"]["userID"]
                    session["user"] = {
                        "user_id": response["data"]["userID"],
                        "email": email
                    }
                    # User-role used by security section
                    session["user_role"] = role
                    
                    return jsonify({"message": "Registration successful!"}), 201
                
                if response["status"] == "error":
                    if response["error"] == "email already registered":
                        return jsonify({"message": "Email already registered."}), 400
                    return jsonify({"message": response.get("error", "Unknown error")}), 400

            raise Exception("unknown error during registration")

        except Exception as e:
            print(f"Error during registration: {e}")
            return jsonify({"message": "An error occurred during registration."}), 500