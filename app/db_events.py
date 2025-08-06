from sqlalchemy import insert
from app.models import Notification, Reservation, Admin
from app.extensions import db


def register_db_event_listeners():
    @db.event.listens_for(Reservation, 'before_insert')
    def log_notification(mapper, connection, target):
        # Query all admins
        admins = db.session.query(Admin.id).all()
        
        if not admins:
            return

        notifications = [
            {
                "title": "Reservation Received",
                "message": "%s, booked a reservation(%s) from %s to %s. " % (target.fullname, target.room.name, target.check_out.strftime("%B %d, %Y"), target.check_in.strftime("%B %d, %Y")),
                "user_id": admin.id
            }
            for admin in admins
        ]

        connection.execute(insert(Notification), notifications)
