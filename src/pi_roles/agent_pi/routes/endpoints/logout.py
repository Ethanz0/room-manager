from flask import session

def logout_endpoint(app, config): 
    """Define the logout endpoint."""

    @app.route("/logout", methods=["POST"])
    def logout_user():
        session.clear()
        return {"message": "Logged out successfully"}, 200