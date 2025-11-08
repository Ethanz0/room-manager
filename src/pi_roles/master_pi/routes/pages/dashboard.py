from flask import render_template, session, redirect, url_for

def dashboard_page(app, config):
    """Define route for dashboard page"""
    @app.route("/dashboard")
    def dashboard():
        name = session.get("name", "User")
        
        return render_template(
            "dashboard.html", 
            role="Master", 
            config=config,
            name=name
        )