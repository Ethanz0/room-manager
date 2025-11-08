from flask import render_template

def announcements_page(app, config):
    """Registers the announcements page route."""
    @app.route('/announcements')
    def announcements():
        # Logic to fetch and display announcements
        return render_template('announcements.html')