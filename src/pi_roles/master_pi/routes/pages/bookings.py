from datetime import datetime
from flask import flash, redirect, render_template, url_for, request, send_file
from common.communication.socket_client import JsonSocketClient

def bookings_page(app, config):
    @app.route("/bookings")
    def bookings():
        
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "get_bookings"
            })
        
        if response.get("status") == "success":
            bookings = response.get("data", [])
        else:
            bookings = []
        
        return render_template("bookings.html", role="Master", config=config, bookings=bookings)
