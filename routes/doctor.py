from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.doctor_controller import DoctorController

doctor_blueprint = Blueprint("doctor", __name__)

@doctor_blueprint.route("", methods=["GET"])
@jwt_required()
def list_doctors():
    return DoctorController.list_doctors()

@doctor_blueprint.route("/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor(doctor_id):
    return DoctorController.get_doctor(doctor_id)

@doctor_blueprint.route("/availability/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_availability(doctor_id):
    return DoctorController.get_availability(doctor_id)

