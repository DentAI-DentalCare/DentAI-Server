from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from controllers.auth_controller import AuthController

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    return AuthController.signup()

@auth_blueprint.route("/login", methods=["POST"])
def login():
    return AuthController.login()

@auth_blueprint.route("/logout", methods=["POST"])

@jwt_required()
def logout():
    return AuthController.logout()

@auth_blueprint.route("/password/send-code", methods=["POST"])
def send_reset_code():
    return AuthController.send_reset_code()

@auth_blueprint.route("/password/verify-code", methods=["POST"])
def verify_reset_code():
    return AuthController.verify_reset_code()

@auth_blueprint.route("/password/reset", methods=["POST"])
def reset_password():
    return AuthController.reset_password()

@auth_blueprint.route("/password/change", methods=["POST"])
def change_password():
    return AuthController.change_password()