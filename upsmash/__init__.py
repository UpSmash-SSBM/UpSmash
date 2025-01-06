from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from upsmash.config import Config

db = SQLAlchemy()

def create_min_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def create_full_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    from upsmash.main.routes import main
    from upsmash.users.routes import users
    from upsmash.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
