from flask import session, redirect, url_for


def logout_endpoint(app, config):
    """Define route for logout"""

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))
