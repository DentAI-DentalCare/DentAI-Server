from flask import Blueprint
from flask_jwt_extended import jwt_required
from controllers.caries_detection_controller import CariesDetectionController

caries_detection_blueprint = Blueprint("caries_detection_blueprint", __name__)


@caries_detection_blueprint.route("/YOLOv8/<YOLOv8_model>", methods=["POST"])
@jwt_required()
def classify_YOLOv8(YOLOv8_model):
    return CariesDetectionController._classify_YOLOv8(YOLOv8_model)

@caries_detection_blueprint.route("/YOLOv8/vertices", methods=["POST"])
@jwt_required()
def classify_YOLOv8_vertices():
    return CariesDetectionController._classify_YOLOv8_vertices()


@caries_detection_blueprint.route("/YOLO-NAS", methods=["POST"])
@jwt_required()
def classify_YOLO_NAS():
    return CariesDetectionController._classify_YOLO_NAS()

@caries_detection_blueprint.route("/YOLO-NAS/vertices", methods=["POST"])
@jwt_required()
def classify_YOLO_NAS_vertices():
    return CariesDetectionController._classify_YOLO_NAS_vertices()


# @caries_detection_blueprint.route("/efficientnet/<efficientnet_model>", methods=["POST"])
# @jwt_required()
# def classify_efficientnet_dynamic(efficientnet_model):
#     return CariesDetectionController.classify_efficientnet(efficientnet_model)


# @caries_detection_blueprint.route("/YOLOv8-efficientnet/<efficientnet_model>", methods=["POST"])
# @jwt_required()
# def classify_YOLOv8_to_efficientnet_dynamic(efficientnet_model):
#     return CariesDetectionController.detect_and_classify_YOLOv8_to_efficientnet(efficientnet_model)
