from .bookings import bookings_endpoints
from .test import test_endpoints
from .registration import register_endpoints
from .login import login_endpoints
from .logout import logout_endpoint
from .security import security_endpoints

def create_endpoints(app, config):
    """Register all endpoint groups with the Flask app."""
    bookings_endpoints(app, config)
    test_endpoints(app, config)
    register_endpoints(app, config)
    login_endpoints(app, config)
    logout_endpoint(app, config)
    security_endpoints(app, config)
