from .login import login_page
from .dashboard import dashboard_page
from .users import users_page
from .logs import logs_page
from .bookings import bookings_page
from .rooms import rooms_pages
from .announcements import announcements_page

def create_pages(app, config):
    """Define routes for pages for the Flask app"""
    login_page(app, config)
    dashboard_page(app, config)
    users_page(app, config)
    logs_page(app, config)
    bookings_page(app, config)
    rooms_pages(app, config)
    announcements_page(app, config)
