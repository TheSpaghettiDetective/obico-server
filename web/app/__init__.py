from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config

web_app = Flask(
        __name__,
        # Tricks to integrate with webpack
        template_folder="../public",
        static_folder="../public",
        static_url_path=""
        )

web_app.config.from_object(Config)
web_app.config['DEBUG'] = True
db = SQLAlchemy(web_app)
migrate = Migrate(web_app, db)

from app import routes, models
from app.models import *

@web_app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Printer': Printer, 'Detection': Detection}
