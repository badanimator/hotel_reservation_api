from flask_restful import Resource, abort, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity, 
    jwt_required, get_jwt
)
from app.data_schema import AdminSchema, LoginSchema
from app.models import Admin, TokenBlocklist
from app.constant import HTTPStatus
from app.extensions import db

class RegisterView(Resource):
    def post(self):
        # parse json
        form = request.form.to_dict() if request.form else request.json
        admin_schema = AdminSchema()

        # validate user data
        if errors:= admin_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, message=errors)

        user = admin_schema.load(form, session=db.session)
        db.session.add(user)
        db.session.commit()

        # generage token
        access_token = create_access_token(identity=str(user.id)) 
        refresh_token = create_refresh_token(identity=str(user.id))
        return {"access_token": access_token, "refresh_token": refresh_token}, HTTPStatus.CREATED


class LoginView(Resource):
    def post(self):
        form = request.form.to_dict() if request.form else request.json
        login_data = LoginSchema()

        if errors:=login_data.validate(form):
            abort(HTTPStatus.BAD_REQUEST, message=errors)

        # get user data
        login = login_data.load(form)
        username = login.get("username")
        password = login.get('password')
        
        user = Admin.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            access_token = create_access_token(identity=str(user.id)) 
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {"access_token": access_token, "refresh_token": refresh_token}, HTTPStatus.OK
        abort(HTTPStatus.NOT_FOUND, message='Invalid Username or Password')

class LogoutView(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        blocklist = TokenBlocklist(jti=jti)
        db.session.add(blocklist)
        db.session.commit()
        return {"message": "User logged out"}

class RefreshTokenView(Resource):
    @jwt_required(refresh=True)
    def post(self):
        # parse json
        user_id = get_jwt_identity()
        user = Admin.query.get(user_id)
        access_token = create_access_token(identity=str(user.id)) 
        return {'access_token': access_token}, HTTPStatus.OK
    