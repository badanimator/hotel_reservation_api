from flask_restful import Resource, abort, request
from app.data_schema import SendUsMessageSchema
from app.constant import HTTPStatus
from flask_mail import Message
from app.extensions import mail


class SendUsMessageView(Resource):
    def post(self):
        form = request.form.to_dict() if request.form else request.json
        message_schema = SendUsMessageSchema()

        # validate user data
        if errors:= message_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, message=errors)
            
        fullname = form.get("fullname")
        email = form.get("email")
        message = form.get("message")
        subject = form.get("subject")

        body = f"Name: {fullname}\nEmail: {email}\n\nMessage:\n{message}"
        msg = Message(subject=subject, recipients=[email], body=body)

        try:
            mail.send(msg)
        except Exception as err:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=err.args)

        return {"message": "%s, Your message has been send!" % fullname.title()}, HTTPStatus.CREATED
