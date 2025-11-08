from flask import render_template

def registration_pages(app, config):
    """Define route for registration page"""
    @app.route("/registration")
    def registration():
        return render_template("registration.html", role="Agent", config=config)