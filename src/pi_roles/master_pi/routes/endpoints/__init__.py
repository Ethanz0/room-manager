from .testing import testing_endpoints
from .login import login_endpoint
from .logout import logout_endpoint
from .user import user_endpoint
from .bookings import booking_endpoint
from .logs import logs_endpoint
from .rooms import rooms_endpoints
from .publish_announcement import publish_announcement_endpoint

def create_endpoints(app, config):
    """Define routes for endpoints for the Flask app"""
    login_endpoint(app, config)
    logout_endpoint(app, config)
    user_endpoint(app, config)
    # For testing purposes only
    testing_endpoints(app, config)
    booking_endpoint(app, config)
    logs_endpoint(app, config)
    rooms_endpoints(app, config)
    publish_announcement_endpoint(app, config)