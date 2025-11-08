from flask import render_template, session

def booking_pages(app, config):
    """Define routes for booking pages"""
    @app.route("/book-room")
    def book_room_page():
        agent_role = session["user_role"]
        return render_template("book-room.html", role="Agent", agent_role=agent_role, config=config)
    
    @app.route("/booked-rooms")
    def booked_rooms_page():
        agent_role = session["user_role"]
        return render_template("booked-rooms.html", role="Agent", agent_role=agent_role, config=config)