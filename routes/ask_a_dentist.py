from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.ask_a_dentist_controller import AskADentistController

ask_a_dentist_blueprint = Blueprint("ask_a_dentist", __name__)

# POST: Send a message or image to another user (creates thread if not exists)
@ask_a_dentist_blueprint.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    return AskADentistController.send_message()

# GET: Fetch all users who sent me messages, with last message and date
@ask_a_dentist_blueprint.route("/my-conversations", methods=["GET"])
@jwt_required()
def get_my_conversations():
    return AskADentistController.get_my_conversations()

# GET: Get all messages between me and a specific user (chat view)
@ask_a_dentist_blueprint.route("/thread/<int:user_id>", methods=["GET"])
@jwt_required()
def get_thread_with_user(user_id):
    return AskADentistController.get_thread_with_user(user_id)


# GET: Get all messages between me and a specific user (chat view)
@ask_a_dentist_blueprint.route("/doctors-info", methods=["GET"])
@jwt_required()
def get_all_doctors_info():
    return AskADentistController.get_all_doctors_info()

