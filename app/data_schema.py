from app.models import *
from marshmallow import fields, validate, validates, EXCLUDE, ValidationError
from app.fields import PhoneNumberField, HumanTime
from app.extensions import ma


class NotificationSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Notification
        unknown = EXCLUDE

    id = fields.Integer()
    title = fields.String()
    message = fields.String()
    is_read = fields.Boolean()
    created_at = HumanTime()


class AdminSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Admin
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer(load_only=True)
    fullname = fields.String(dump_only=True)
    username = fields.String()
    created_at = HumanTime(dump_only=True)
    updated_at = HumanTime(dump_only=True)
    # notifications = fields.Nested(NotificationSchema, many=True)


class AmenitySchema(ma.SQLAlchemySchema):
    class Meta():
        model = Amenity
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer()
    name = fields.String()

    def get_instance(self, data):
        amenity = Amenity.query.filter_by(name=data["name"]).first()
        return amenity  
        

class RoomImageSchema(ma.SQLAlchemySchema):
    class Meta():
        model = RoomImage
        unknown = EXCLUDE

    id = fields.Integer()
    unique_filename = fields.String()
    filename = fields.String()
    is_cover = fields.Boolean()
    url = fields.Method("get_image_url")

    def get_image_url(self, data, **kwargs):
        from flask_restful import url_for

        return  url_for(
            "room_image", 
            unique_filename=data.unique_filename, 
            _external=True
        )
    

class RoomSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Room
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer()
    name = fields.String(required=True)
    price = fields.Number(required=True)
    description = fields.String()
    created_at = HumanTime(dump_only=True)
    updated_at = HumanTime(dump_only=True)
    images = fields.Nested(RoomImageSchema, many=True, dump_only=True)
    amenities = fields.List(fields.Pluck(AmenitySchema, field_name="name"))

    @validates("name")
    def validate_name(self, name:str):
        method = self.context.get("method", "GET")
        room_id = self.context.get("room_id")

        existing_name = Room.query.filter(Room.name.ilike(name)).first()

        if method == "POST":
            if existing_name:
                raise ValidationError(f"{name.title()} is already taken.")
        
        elif method == "PATCH":
            if existing_name and existing_name.id != room_id:
                raise ValidationError(f"{name.title()} is already taken.")


class ReservationSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Reservation
        load_instance = True
        unknown = EXCLUDE

    id = fields.Integer(dump_only=True)
    check_in = fields.Date(required=True)
    check_out = fields.Date(required=True)
    guest_count = fields.Integer(load_default=1)
    fullname = fields.String(required=True)
    email = fields.String(required=True)
    phone_number = PhoneNumberField(required=True)
    room_id = fields.Integer(required=True, load_only=True)
    created_at = HumanTime(dump_only=True)
    updated_at = HumanTime(dump_only=True)
    room = fields.Nested(RoomSchema, dump_only=True)


class LoginSchema(ma.Schema):
    class Meta():
        unknown=EXCLUDE

    username = fields.String(required=True)
    password = fields.String(required=True)

class PaginationRequestSchema(ma.Schema):
    class Meta:
        unknown=EXCLUDE
        
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1))


class MetaSchema(ma.Schema):
    class Meta():
        unknown=EXCLUDE

    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=10)
    pages = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()
    next_num = fields.Integer()
    prev_num = fields.Integer()
    has_next = fields.Boolean()
    has_prev = fields.Boolean()
