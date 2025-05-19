from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.caries_detection_controller import CariesDetectionController

caries_detection_blueprint = Blueprint("caries_detection_blueprint", __name__)


@caries_detection_blueprint.route("/yolov8/<yolov8_model>", methods=["POST"])
@jwt_required()
def classify_yolov8(yolov8_model):
    return CariesDetectionController._classify_yolov8(yolov8_model)

@caries_detection_blueprint.route("/yolov8/vertices", methods=["POST"])
@jwt_required()
def classify_yolov8_vertices():
    return CariesDetectionController._classify_yolov8_vertices()



# @caries_detection_blueprint.route("/efficientnet/<efficientnet_model>", methods=["POST"])
# @jwt_required()
# def classify_efficientnet_dynamic(efficientnet_model):
#     return CariesDetectionController.classify_efficientnet(efficientnet_model)


# @caries_detection_blueprint.route("/yolov8-efficientnet/<efficientnet_model>", methods=["POST"])
# @jwt_required()
# def classify_yolov8_to_efficientnet_dynamic(efficientnet_model):
#     return CariesDetectionController.detect_and_classify_yolov8_to_efficientnet(efficientnet_model)
