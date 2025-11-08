from flask import request, redirect, url_for, flash, session, render_template
from common.communication.socket_client import JsonSocketClient

def login_endpoint(app, config):
    """Define route for login"""
    @app.route("/login", methods=["POST"])
    def login():
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Validate required fields
        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for("index"))
        
        # Send login request to backend
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "login_admin",
                "email": email,
                "password": password,
            })
        
        if response.get("status") == "success":
            # Store user info in session
            user = response.get("user")
            session["user"] = user.get("user_id")
            session["name"] = user.get("first_name") + " " + user.get("last_name")
            session["user_role"] = "Admin"

            return redirect(url_for("dashboard"))
        else:
            error_msg = response.get("message", "Invalid credentials")
            flash(error_msg, "danger")
            return redirect(url_for("index"))
        