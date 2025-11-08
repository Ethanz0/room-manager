from flask import request, redirect, send_file, url_for, flash
from common.communication.socket_client import JsonSocketClient
from io import BytesIO
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def logs_endpoint(app, config):  
    @app.route("/logs/download")
    def download_report():
        log_type = request.args.get('type', '')
        try:
            with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
                response = client.send_request({
                    "action": "get_logs",
                    "log_type": log_type
                })
            
            if response.get("status") != "success":
                flash("Error gettings logs", "danger")
                return redirect(url_for("logs"))    
            
            logs = response.get("logs", [])
            if not logs:
                flash("No logs found", "danger")
                return redirect(url_for("logs"))    
            
            types = [log['type'] for log in logs]
            type_counts = Counter(types)
            
            plt.figure(figsize=(12, 8))
            plt.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
            plt.title(f'Usage Logs Report: ({len(logs)} Total Logs)')

            # Save file temporarily
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300)
            img_buffer.seek(0)
            plt.close()
            
            # Return the image
            return send_file(
                img_buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name='Usage_Report.png'
            )
        except Exception as e:
            flash("Error fetching log data", "danger")
            return redirect(url_for("logs"))