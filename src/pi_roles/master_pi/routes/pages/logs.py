from flask import flash, redirect, render_template, url_for, request, send_file
from common.communication.socket_client import JsonSocketClient
from io import BytesIO
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def logs_page(app, config):
    @app.route("/logs")
    def logs():
        log_type = request.args.get('type', '')
        
        with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
            response = client.send_request({
                "action": "get_logs",
                "log_type": log_type
            })
            
        if response.get("status") == "success":
            logs = response.get("logs", [])
        else:
            logs = []
            
        return render_template("logs.html", role="Master", config=config, logs=logs, log_type=log_type)
    

