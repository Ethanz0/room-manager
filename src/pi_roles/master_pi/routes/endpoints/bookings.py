from collections import defaultdict
from datetime import datetime
from flask import redirect, send_file, url_for, flash
from common.communication.socket_client import JsonSocketClient
from io import BytesIO
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def booking_endpoint(app, config):    
    @app.route("/bookings/download")
    def download_booking_report():
        try:
            # Get booking statistics via socket connection
            with JsonSocketClient(config["socket_host"], config["socket_port"]) as client:
                response = client.send_request({
                    "action": "get_booking_stats"
                })
            
            if response.get("status") != "success":
                flash("Error fetching booking stats", "danger")
                return redirect(url_for("bookings"))
            
            stats = response.get("data", [])
            
            if not stats:
                flash("No Bookings Found", "danger")
                return redirect(url_for("bookings"))
            
            # Organize data by room
            room_data = defaultdict(lambda: {"dates": [], "counts": []})
            
            for stat in stats:
                if stat['date']:
                    room_name = stat['room_name']
                    date = datetime.strptime(stat['date'], '%Y-%m-%d')
                    count = stat['count']
                    
                    room_data[room_name]["dates"].append(date)
                    room_data[room_name]["counts"].append(count)
            
            # Convert to cumulative counts
            for room_name, data in room_data.items():
                if data["counts"]:
                    cumulative = []
                    total = 0
                    for count in data["counts"]:
                        total += count
                        cumulative.append(total)
                    room_data[room_name]["counts"] = cumulative
            
            # Create line graph
            plt.figure(figsize=(12, 6))
            
            # Plot a line for each room
            for room_name, data in room_data.items():
                if data["dates"]:
                    plt.plot(data["dates"], data["counts"], marker='o', label=room_name)
            
            plt.xlabel('Date')
            plt.ylabel('Cumulative Bookings')
            plt.title('Cumulative Room Bookings Over Time')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            # Save file temporarily
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300)
            img_buffer.seek(0)
            plt.close()
            
            return send_file(
                img_buffer,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'Bookings_Report.png'
            )
            
        except Exception as e:
            flash("Error fetching booking stats", "danger")
            return redirect(url_for("bookings"))