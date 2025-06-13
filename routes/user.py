from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.user_controller import UserController

user_blueprint = Blueprint("user", __name__)

# GET /api/user/profile
@user_blueprint.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    return UserController.get_profile()

# PUT /api/user/profile
@user_blueprint.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    return UserController.update_profile()

# DELETE /api/user/delete
@user_blueprint.route("/delete/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    return UserController.delete_account()

# POST /api/user/upload/teeth-image
@user_blueprint.route("/upload/teeth-image", methods=["POST"])
@jwt_required()
def upload_teeth_image():
    return UserController.upload_teeth_image()

# POST /api/user/upload/teeth-image
@user_blueprint.route("/delete/teeth-image/<image_id>", methods=["DELETE"])
@jwt_required()
def delete_teeth_image(image_id):
    return UserController.delete_teeth_image(image_id)

# POST /api/user/upload/profile-image
@user_blueprint.route("/upload/profile-image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    return UserController.upload_profile_image()

# POST /api/user/upload/profile-image
@user_blueprint.route("/delete/profile-image", methods=["DELETE"])
@jwt_required()
def delete_profile_image():
    return UserController.delete_profile_image()

# GET /api/user/images
@user_blueprint.route("/teeth-images", methods=["GET"])
@jwt_required()
def get_images():
    return UserController.get_teeth_images()

# GET /api/user/image/<id>
@user_blueprint.route("/image/<int:image_id>", methods=["GET"])
@jwt_required()
def get_image_by_id(image_id):
    return UserController.get_image_by_id(image_id)
