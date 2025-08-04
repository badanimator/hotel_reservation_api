from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils.observer import observes
from datetime import datetime
from slugify import slugify
from app.extensions import db



room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'))
)

class Amenity(db.Model):
    __tablename__ = 'amenity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)


class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    notifications = db.relationship('Notification', backref='admin', lazy='dynamic', cascade='all, delete-orphan')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        self.secret = password
        return check_password_hash(self.password_hash, password)
    

class Reservation(db.Model):
    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer, default=1)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    room = db.relationship('Room', back_populates='reservations', lazy='joined')


class RoomImage(db.Model):
    __tablename__ = "room_image"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id", ondelete="CASCADE"))
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255))
    unique_filename = db.Column(db.String(255))
    is_cover = db.Column(db.Boolean, default=False)

    @observes('filename')
    def compute_slug(self, filename):
        self.unique_filename = self.generate_unique_filename(filename)
        

    def generate_unique_filename(self, title):
        while True:
            base_slug = slugify(title)
            unique_filename = base_slug
            counter = 1
            while RoomImage.query.filter_by(unique_filename=unique_filename).first():
                unique_filename = f"{base_slug}-{counter}"
                counter += 1
            return unique_filename



class Room(db.Model):
    __tablename__ = "room"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    price = db.Column(db.Numeric(10, 2), default=0.0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    images = db.relationship("RoomImage", backref="room", cascade="all, delete-orphan", order_by="RoomImage.is_cover.desc()")
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')
    reservations = db.relationship('Reservation', back_populates="room", lazy='dynamic')


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    def mark_as_read(self):
        self.is_read = True
        db.session.flush()

    @staticmethod
    def mark_all_as_read(user_id):
        for item in Notification.query.filter_by(user_id=user_id).all():
            item.mark_as_read()
        db.session.flush()
    
    def remove_notification(self):
        n = Notification.query.get(self.id)
        db.session.delete(n)
        db.session.commit()


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<TokenBlocklist %r>' % self.id
