from flask import flash, redirect, render_template, url_for
from common.communication.socket_client import JsonSocketClient

def users_page(app, config):
    @app.route("/users")
    def users():

        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({"action": "get_all_users"})
        
        if response.get("status") == "success":
            all_users = response.get("users", [])
        else:
            error_msg = response.get("message", "Failed to get users")
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for("dashboard"))  
        filtered_users = []
        
        for user in all_users:
            if user['role'] != 'Admin':
                filtered_users.append(user)

        return render_template("users.html", role="Master", config=config, users=filtered_users)
        
    @app.route("/users/<int:user_id>/edit")
    def edit_user_page(user_id):
        """Edit user form"""
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "get_user",
                "user_id": user_id
            })
        
        if response.get("status") == "success":
            user = response.get("user", {}) 
            
            if not user:
                return redirect(url_for("users"))
            
            return render_template("edit_user.html", user=user, config=config)
        else:
            error_msg = response.get("message", "Failed to edit user")
            flash(f"Error: {error_msg}", "danger")
            return redirect(url_for("users"))

        
    @app.route("/users/create")
    def create_security_page():
        """Create Security Staff"""
            
        return render_template("create_security.html", config=config)

        


