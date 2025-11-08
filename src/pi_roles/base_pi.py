import os 
from abc import ABC, abstractmethod

from flask import Flask

class BasePi(ABC):
    """ BasePi class to create Flask app for different Pi roles """
    @abstractmethod
    def create_routes(self, app, config):
        """ Define routes for the Flask app """


    def create_app(self, config, app_dir=None, app_name=__name__):
        """ Create and configure the Flask app """
        base_dir = os.path.dirname(os.path.abspath(app_dir))
        template_dir = os.path.join(base_dir, "templates")
        static_dir = os.path.join(base_dir, "static")
        app = Flask(app_name, template_folder=template_dir, static_folder=static_dir)
        self.create_routes(app, config)
        return app
        