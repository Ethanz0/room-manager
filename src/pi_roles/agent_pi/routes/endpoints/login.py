from flask import request, jsonify, session
from common.communication.socket_client import JsonSocketClient

def validate_fields(data, required_fields: list[str]) -> list[str]:
    """Returns a list of fields that are missing from the data"""
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    return missing_fields

def login_endpoints(app, config):
    """Define the login endpoint."""

    @app.route("/login", methods=["POST"])
    def login_user():
        data = request.get_json()

        if not data:
            return jsonify({"message": "Invalid JSON data"}), 400

        missing_fields = validate_fields(data, ["email", "password"])
        if len(missing_fields) > 0:
            return jsonify({"message": "Missing fields: " + str(missing_fields)}), 400

        email = data["email"]
        password = data["password"]

        print(f"Logging in user {email} through the Master Pi...")

        try:
            with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
                response = client.send_request({
                    "action": "login_user",
                    "email": email,
                    "password": password
                })
                print("Response from socket server:", response)

                if response["status"] == "success":
                    user_data = response["data"]
                    
                    session["user_email"] = email
                    session["user_id"] = user_data["userID"]
                    session["user"] = {
                        "user_id": user_data["userID"],
                        "email": user_data["email"],
                        "first_name": user_data["firstName"],
                        "last_name": user_data["lastName"],
                        "role": user_data["role"],
                        "qr_code_token": user_data["qrCodeToken"]
                    }
                    # User-role used by security section
                    session["user_role"] = user_data["role"]

                    return jsonify({
                        "message": "Login successful!",
                        "user_id": user_data["userID"],
                        "first_name": user_data["firstName"],
                        "last_name": user_data["lastName"],
                        "email": user_data["email"],
                        "role": user_data["role"]
                    }), 200
                
                if response["status"] == "error":
                    if response["error"] == "invalid credentials":
                        return jsonify({"message": "Invalid email or password."}), 401
                    return jsonify({"message": response.get("error", "Unknown error")}), 400

            raise Exception("unknown error during login")

        except Exception as e:
            print(f"Error during login: {e}")
            return jsonify({"message": "An error occurred during login."}), 500
    
    @app.route("/login/qr-token", methods=["GET"])
    def get_qr_code_token():
        if "user" not in session:
            return jsonify({"message": "User not logged in"}), 401
        
        user = session["user"]
        qr_code_token = user.get("qr_code_token")

        if not qr_code_token:
            return jsonify({"message": "QR code token not found"}), 404

        return jsonify({
            "message": "QR code token retrieved successfully",
            "qr_code_token": qr_code_token,
            "user_id": user["user_id"]
        }), 200
    
    @app.route("/qrcode-login", methods=["POST"])
    def qrcode_login():
        data = request.get_json()

        if not data:
            return jsonify({"message": "Invalid JSON data"}), 400

        missing_fields = validate_fields(data, ["userID", "token"])
        if len(missing_fields) > 0:
            return jsonify({"message": "Missing fields: " + str(missing_fields)}), 400

        user_id = data["userID"]
        token = data["token"]

        print(f"Logging in user {user_id} via QR Code through the Master Pi...")

        try:
            with JsonSocketClient(config.get("master_host"), config.get("master_socket_port")) as client:
                response = client.send_request({
                    "action": "qr_code_login",
                    "userID": user_id,
                    "token": token
                })
                print("Response from socket server:", response)

                if response["status"] == "success":
                    user_data = response["data"]
                    
                    session["user_id"] = user_data["userID"]
                    session["user"] = {
                        "user_id": user_data["userID"],
                        "email": user_data["email"],
                        "first_name": user_data["firstName"],
                        "last_name": user_data["lastName"],
                        "role": user_data["role"],
                        "qr_code_token": user_data["qrCodeToken"]
                    }
                    session["user_role"] = user_data["role"]

                    return jsonify({
                        "message": "QR Code Login successful!",
                    }), 200
                
                if response["status"] == "error":
                    if response["error"] == "invalid credentials":
                        return jsonify({"message": "Invalid userID or token."}), 401
                    return jsonify({"message": response.get("error", "Unknown error")}), 400
            
        except Exception as e:
            print(f"Error during QR code login: {e}")
            return jsonify({"message": "An error occurred during QR code login."}), 500


