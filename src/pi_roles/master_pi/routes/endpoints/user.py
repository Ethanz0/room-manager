from flask import redirect, url_for, request, flash, render_template
from common.communication.socket_client import JsonSocketClient

def user_endpoint(app, config):
    @app.route("/users/<int:user_id>/update", methods=["POST"])
    def update_user(user_id):
        """Update user"""
        # Get form data
        user_data = {
            "user_id": user_id,
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        
        # Validate required fields
        if not all([user_data["first_name"], user_data["last_name"],
                    user_data["email"], user_data["password"]]):
            flash("All required fields must be filled", "danger")
            return render_template("edit_user.html", user=user_data, config=config)
        
        # Send update request to backend
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "update_user",
                "user_id": user_id,
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "email": user_data["email"],
                "password": user_data["password"],
            })
            
            if response.get("status") == "success":
                flash("User updated successfully", "success")
                return redirect(url_for("users"))
            else:
                error_msg = response.get("message", "Failed to update user")
                flash(f"Error: {error_msg}", "danger")
                return render_template("edit_user.html", user=user_data, config=config)
    
    @app.route("/users/<int:user_id>/delete")
    def delete_user(user_id):
        """Delete user"""
        # Send delete request to backend
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "delete_user",
                "user_id": user_id
            })
            
            if response.get("status") == "success":
                flash("User deleted successfully", "success")
                return redirect(url_for("users"))
            else:
                error_msg = response.get("message", "Failed to delete user")
                flash(f"Error: {error_msg}", "danger")
                return redirect(url_for("users"))
            
    @app.route("/users/create", methods = ["POST"])
    def create_security():
        user_data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "role": "Security"
        }
        """Create new security staff"""
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "create_user",
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "email": user_data["email"],
                "password": user_data["password"],
                "role": user_data["role"]
            })

            if response.get("status") == "success":
                flash("Security staff created successfully", "success")
                return redirect(url_for("users"))
            else:
                error_msg = response.get("message", "Failed to create security staff")
                flash(f"Error: {error_msg}", "danger")
                return redirect(url_for("users"))
