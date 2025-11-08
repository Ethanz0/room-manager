from flask import render_template

def login_pages(app, config):
    """Define route for login page"""

    @app.route("/login")
    def login():
        return render_template("login.html", role="Agent", config=config)
    
    @app.route("/qr-code-login")
    def qr_code_login():
        return render_template("qr-code-login.html", role="Agent", config=config)