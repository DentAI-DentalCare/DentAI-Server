from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.caries_detection_controller import CariesDetectionController

caries_detection_blueprint = Blueprint("caries_detection_blueprint", __name__)


@caries_detection_blueprint.route("/yolov8/<yolov8_model>", methods=["POST"])
@jwt_required()
def classify_yolov8(yolov8_model):
    return CariesDetectionController._classify_yolov8(yolov8_model)


# @caries_detection_blueprint.route("/yolov8m/100", methods=["POST"])
# @jwt_required()
# def classify_yolov8m_100():
#     return CariesDetectionController._classify_yolov8("yolov8m_100epochs.pt")


# @caries_detection_blueprint.route("/yolov8m/150", methods=["POST"])
# @jwt_required()
# def classify_yolov8m_150():
#     return CariesDetectionController._classify_yolov8("yolov8m_150mepochs.pt")


# @caries_detection_blueprint.route("/yolov8l/50", methods=["POST"])
# @jwt_required()
# def classify_yolov8l_50():
#     return CariesDetectionController._classify_yolov8("yolov8l_50epochs.pt")


# @caries_detection_blueprint.route("/yolov8l/150", methods=["POST"])
# @jwt_required()
# def classify_yolov8l_150():
#     return CariesDetectionController._classify_yolov8("yolov8l_150epochs.pt")


@caries_detection_blueprint.route("/yolov8-efficientnet/<efficientnet_model>", methods=["POST"])
@jwt_required()
def classify_yolov8_to_efficientnet_dynamic(efficientnet_model):
    return CariesDetectionController.detect_and_classify_yolov8_to_efficientnet(efficientnet_model)
