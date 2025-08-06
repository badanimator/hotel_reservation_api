from io import BytesIO
from flask import send_file
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required
from app.constant import HTTPStatus
from app.data_schema import RoomSchema, PaginationRequestSchema, MetaSchema                                                                                                                                           
from app.models import Room, RoomImage
from app.extensions import db
from app.utils import compress_image, is_image, is_max_size_exceeded

class RoomView(Resource):
    def get(self):
        room_schema = RoomSchema(many=True)
        pagination_schema = PaginationRequestSchema()
        meta_schema = MetaSchema()

        rooms = Room.query.filter(Room.images.any()).order_by(
            Room.created_at.desc()
        ).paginate(**pagination_schema.dump(request.args))
        
        return {
            "items":room_schema.dump(rooms.items),
            "meta": meta_schema.dump(rooms)
        }
    
    
    @jwt_required()
    def post(self):
        form = request.form.to_dict() if request.form else request.json
        room_schema = RoomSchema(context={"method":request.method})

        if errors:= room_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, errors=errors)

        room = room_schema.load(form, session=db.session)
        db.session.add(room)
        db.session.commit()
        return {"message":"%s has been add." % room.name.title()}, HTTPStatus.CREATED
    
    
    @jwt_required()
    def patch(self, id=None):
        form = request.form.to_dict() if request.form else request.json
        room = Room.query.get_or_404(id)
        room_schema = RoomSchema(context={"method":request.method, "room_id":room.id})

        if errors:= room_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, errors=errors)

        room = room_schema.load(form, session=db.session, instance=room)

        db.session.commit()
        return {"message":"%s has been updated." % room.name.title()}
    

    @jwt_required()
    def delete(self, id=None):
        room = Room.query.get_or_404(id)

        if room.reservations.count() > 0:
            abort(HTTPStatus.BAD_REQUEST, message="This room has reservations. Action aborted")

        db.session.delete(room)
        db.session.commit()
        return {"message":"Room has been removed!"}


class RoomImageView(Resource):
    def get(self, unique_filename=None):
        image = RoomImage.query.filter_by(unique_filename=unique_filename).first_or_404()

        return send_file(
            BytesIO(image.data),
            mimetype=image.mimetype,
            download_name=image.filename
        )

    @jwt_required()
    def post(self, id=None):
        room = Room.query.get_or_404(id)
        images = request.files.getlist("image")

        image_objs = []
        for image in images:
            if is_image(image) and not is_max_size_exceeded(image):
                data, mime, filename = compress_image(image)
                image_objs.append(RoomImage(
                    room_id=room.id,
                    data=data,
                    mimetype=mime,
                    filename=filename
                ))
        
        db.session.add_all(image_objs)
        db.session.commit()
        return {"message":"%d added." % images.__len__()}, HTTPStatus.CREATED
    
    @jwt_required()
    def delete(self, id=None):
        image = RoomImage.query.get_or_404(id)
        db.session.delete(image)
        db.session.commit()
        return {"message":"Image has been removed!"}