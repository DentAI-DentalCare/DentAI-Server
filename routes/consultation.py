from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.consultation_controller import ConsultationController

consultation_blueprint = Blueprint("consultation", __name__)

# POST: Send a message or image to another user (creates thread if not exists)
@consultation_blueprint.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    return ConsultationController.send_message()

# GET: Fetch all users who sent me messages, with last message and date
@consultation_blueprint.route("/my-conversations", methods=["GET"])
@jwt_required()
def get_my_conversations():
    return ConsultationController.get_my_conversations()

# GET: Get all messages between me and a specific user (chat view)
@consultation_blueprint.route("/thread/<int:user_id>", methods=["GET"])
@jwt_required()
def get_thread_with_user(user_id):
    return ConsultationController.get_thread_with_user(user_id)


# GET: Get all messages between me and a specific user (chat view)
@consultation_blueprint.route("/doctors-info", methods=["GET"])
@jwt_required()
def get_all_doctors_info():
    return ConsultationController.get_all_doctors_info()

