from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.data_schema import NotificationSchema, MetaSchema
from app.models import Notification
from app.constant import HTTPStatus

class NotificationsView(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        args = request.args.to_dict()
        data_schema = NotificationSchema(many=True)
        meta_schema = MetaSchema()

        if errors:= meta_schema.validate(args):
            abort(HTTPStatus.BAD_REQUEST, message=errors)

        notifications = Notification.query.filter_by(user_id=user_id).order_by(
            Notification.is_read, 
            Notification.created_at.desc()
        ).paginate(error_out=False, **MetaSchema(context={"method":"post"}).dump(args))
        return {
            "items":data_schema.dump(notifications.items),
            "meta":meta_schema.dump(notifications)
        }
    
    @jwt_required()
    def patch(self):
        form = request.form.to_dict() if request.form else request.json
        if errors:=NotificationSchema().validate(form):
            abort(HTTPStatus.BAD_REQUEST, message=errors)

        notification_id = form.get("id")
        n = Notification.query.get(notification_id)
        n.mark_as_read()
        return {"message":"Success"}, HTTPStatus.OK

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        Notification.mark_all_as_read(user_id)
        return {"message":"Success"}, HTTPStatus.OK