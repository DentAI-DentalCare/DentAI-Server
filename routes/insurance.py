from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.insurance_controller import InsuranceController

insurance_blueprint = Blueprint("insurance", __name__)

@insurance_blueprint.route("/add", methods=["POST"])
@jwt_required()
def add_insurance():
    return InsuranceController.add_insurance()

@insurance_blueprint.route("/all", methods=["GET"])
@jwt_required()
def get_all_insurances():
    return InsuranceController.get_all_insurances()

@insurance_blueprint.route("/update/<int:insurance_id>", methods=["PUT"])
@jwt_required()
def update_insurance(insurance_id):
    return InsuranceController.update_insurance(insurance_id)

@insurance_blueprint.route("/delete/<int:insurance_id>", methods=["DELETE"])
@jwt_required()
def delete_insurance(insurance_id):
    return InsuranceController.delete_insurance(insurance_id)
