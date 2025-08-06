from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required
from app.constant import HTTPStatus
from app.data_schema import ReservationSchema, PaginationRequestSchema, MetaSchema
from app.models import Reservation
from app.extensions import db


class ReservationView(Resource):
    @jwt_required()
    def get(self):
        reservation_schema = ReservationSchema(many=True)
        pagination_schema = PaginationRequestSchema()
        meta_schema = MetaSchema()

        reservations = Reservation.query.order_by(
            Reservation.created_at.desc()
        ).paginate(**pagination_schema.dump(request.args))

        return {
            "items":reservation_schema.dump(reservations.items),
            "meta": meta_schema.dump(reservations)
        }
    
    
    def post(self):
        form = request.form.to_dict() if request.form else request.json
        reservation_schema = ReservationSchema()

        if errors:= reservation_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, errors=errors)

        reservation = reservation_schema.load(form, session=db.session)

        db.session.add(reservation)
        db.session.commit()
        return {
            "message":"".join(
                [
                    "Hello %s, your reservation from %s to %s has been received. " 
                    % (
                        reservation.fullname, 
                        reservation.check_out.strftime("%B %d, %Y"),
                        reservation.check_in.strftime("%B %d, %Y")
                    ),
                    "We’ll confirm your reservation within 24 hours — no payment required upfront. ",
                    "We’ll contact you at your phone number or your email."
                ]
            )
        }, HTTPStatus.CREATED
    

    @jwt_required()
    def patch(self, id=None):
        form = request.form.to_dict() if request.form else request.json
        reservation = Reservation.query.get_or_404(id)
        reservation_schema = ReservationSchema()

        if errors:= reservation_schema.validate(form):
            abort(HTTPStatus.BAD_REQUEST, errors=errors)

        reservation = reservation_schema.load(form, session=db.session, instance=reservation)

        db.session.add(reservation)
        db.session.commit()
        return {"message":"Reservation updated."}
    

    @jwt_required()
    def delete(self, id=None):
        reservation = Reservation.query.get_or_404(id)
        db.session.delete(reservation)
        db.session.commit()
        return {"message":"Reservation removed!"}
