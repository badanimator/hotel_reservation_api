from flask_restful import Resource, request
from app.data_schema import AdminSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import Admin
from app.extensions import db


class AdminProfile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        admin_schema = AdminSchema()

        user = Admin.query.get_or_404(user_id)
        return admin_schema.dump(user)

    @jwt_required()
    def patch(self):
        user_id = get_jwt_identity()
        form = request.form.to_dict() if request.form else request.json
        user_schema = AdminSchema()
        user = Admin.query.get_or_404(user_id)

        user_schema.load(form, instance=user, session=db.session)
        db.session.commit()
        return {"message":"User updated"}
