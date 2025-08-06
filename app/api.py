from app.resources.reservation import ReservationView
from app.resources.notifications import NotificationsView
from app.resources.room import RoomView, RoomImageView
from app.resources.auth import LoginView, RefreshTokenView, LogoutView, RegisterView
from app.resources.account import AdminProfile
from app.resources.message import SendUsMessageView


def register_routes(api):
    api.add_resource(NotificationsView, "/notification")
    api.add_resource(ReservationView, "/reservation", "/reservation/<int:id>")
    api.add_resource(RoomView, "/", "/room", "/room/<int:id>")
    api.add_resource(RoomImageView, "/upload/<int:id>", "/image/<unique_filename>", endpoint="room_image")
    api.add_resource(AdminProfile, "/profile")
    api.add_resource(LoginView, "/login")
    api.add_resource(RefreshTokenView, "/refresh")
    api.add_resource(LogoutView, "/logout")
    api.add_resource(SendUsMessageView, "/message")
