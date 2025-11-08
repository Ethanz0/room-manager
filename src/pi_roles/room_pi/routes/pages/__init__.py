from .home import home_page

def create_pages(app, config):
    """Create page routes for the Flask app"""
    home_page(app, config)
