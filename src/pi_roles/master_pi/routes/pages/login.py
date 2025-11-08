from flask import render_template, redirect, url_for, session


def login_page(app, config):
    """Define the home page route for the Flask app"""

    @app.route("/")
    def index():
        if "user" in session:
            return redirect(url_for("dashboard"))
        return render_template("login.html", role="Master", config=config)
