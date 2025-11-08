from flask import redirect, render_template, session, url_for

def home_pages(app, config):
    """Define route for home pages"""
    @app.route("/")
    def index():
        return render_template("login.html", role="Agent", config=config)

    @app.route("/dashboard")
    def dashboard():
        if "user" not in session:
            return redirect(url_for("login"))
        
        user = session.get("user")
        name = user.get("first_name", "") + " " + user.get("last_name", "")
        
        if session.get("user_role") == "Security":
            return render_template("dashboard-security.html", role="Security", config=config, name=name)
        else:
            return render_template("dashboard.html", role="Agent", config=config, name=name)
