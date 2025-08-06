import os
from flask import Flask
from flask_restful import Api
from app.api import register_routes
from app.db_events import register_db_event_listeners
from app.commands import (
    seed_db, 
    drop_db, 
    seed_admin,
    reset_db
)
from app.extensions import (
    db, 
    cors, 
    migrate, 
    ma, 
    cache, 
    jwt, 
    limiter,
    mail
)
from config import config

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASKCONFIG') or 'development'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    api = Api(app)
    ma.init_app(ma)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    register_routes(api)
    register_db_event_listeners()

    # custom commands
    app.cli.add_command(seed_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(seed_admin)
    app.cli.add_command(reset_db)
    
    return app