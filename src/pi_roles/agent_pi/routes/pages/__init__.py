from .booking import booking_pages
from .home import home_pages
from .login import login_pages
from .registration import registration_pages
from .security import security_pages

def create_pages(app, config):
    """Register all page routes"""
    home_pages(app, config)
    login_pages(app, config)
    registration_pages(app, config)
    booking_pages(app, config)
    security_pages(app, config)
