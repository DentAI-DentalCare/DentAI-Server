from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.appointment_controller import AppointmentController

appointment_blueprint = Blueprint("appointments", __name__)

@appointment_blueprint.route("/", methods=["POST"])
@jwt_required()
def book_appointment():
    return AppointmentController.book_appointment()

@appointment_blueprint.route("/", methods=["GET"])
@jwt_required()
def get_my_appointments():
    return AppointmentController.get_my_appointments()

@appointment_blueprint.route("/<int:appointment_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_appointment(appointment_id):
    return AppointmentController.cancel_appointment(appointment_id)

@appointment_blueprint.route("/<int:appointment_id>/complete", methods=["PUT"])
@jwt_required()
def complete_appointment(appointment_id):
    return AppointmentController.complete_appointment(appointment_id)

@appointment_blueprint.route("/available-timeslots/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_available_timeslots(doctor_id):
    return AppointmentController.get_available_timeslots(doctor_id)
