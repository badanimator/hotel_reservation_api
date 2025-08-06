from flask import jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_migrate import Migrate
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from config import Config
from app.utils import get_limit_payload

def rate_limit_callback(request_limit:RequestLimit):
    payload =  get_limit_payload(request_limit)
    return make_response(jsonify(data=payload, message="Too many requests",), 429)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)
mail = Mail()
cors = CORS(supports_credentials=True)
migrate = Migrate(directory=Config.MIGRATION_PATH, render_as_batch=True)
ma = Marshmallow()
cache = Cache()
jwt = JWTManager()
limiter = Limiter(get_remote_address, storage_uri=Config.CACHE_STORAGE, on_breach=rate_limit_callback)
