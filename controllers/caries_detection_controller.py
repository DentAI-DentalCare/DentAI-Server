from PIL import Image, ImageDraw
import uuid
from io import BytesIO
import os
from flask import current_app, request, jsonify, send_file, make_response
from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
import json

import requests
from flask import Response
# from tensorflow.keras.models import load_model
# from tensorflow.keras.applications.efficientnet import preprocess_input
# from tensorflow.keras.preprocessing.image import img_to_array
from dotenv import load_dotenv
load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID")

class CariesDetectionController:



    @staticmethod
    def detect_and_classify_YOLOv8_to_efficientnet(efficientnet_model):
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        try:
            project_root = current_app.root_path
            temp_dir = os.path.join(project_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)

            # Save input image
            temp_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(temp_dir, temp_filename)
            image_file.save(image_path)

            # Load models
            YOLOv8_path = os.path.join(project_root, "models", "yolov8_detecttctcttttt.pt")
            efficientnet_path = os.path.join(project_root, "models", efficientnet_model)
            if not os.path.exists(YOLOv8_path) or not os.path.exists(efficientnet_path):
                return jsonify({"error": "Model(s) not found"}), 500

            YOLO_model = YOLO(YOLOv8_path)
            efficientnet_model = load_model(efficientnet_path)

            image = cv2.imread(image_path)
            original = image.copy()
            results = YOLO_model(image_path)

            CariesDetectionController.class_labels = {
                0: "Caries Class 1",
                1: "Caries Class 2",
                2: "Caries Class 3",
                3: "Caries Class 4",
                4: "Caries Class 5"
            }

            class_colors = {
                "Caries Class 1": (32, 228, 26),   # green
                "Caries Class 2": (248, 170, 1),   # blue
                "Caries Class 3": (234, 0, 255),  # GBR = Yellow ✅
                "Caries Class 4":  (34, 87, 255),  # orange
                "Caries Class 5": (12, 27, 233),   # red
            }


            detections = []
            class_summary = defaultdict(int)

            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                crop = original[y1:y2, x1:x2]

                # Preprocess crop for EfficientNet
                crop_img = cv2.resize(crop, (224, 224))
                crop_img = Image.fromarray(crop_img)
                crop_img = img_to_array(crop_img)
                crop_img = preprocess_input(crop_img)
                crop_img = np.expand_dims(crop_img, axis=0)

                # Predict
                preds = efficientnet_model.predict(crop_img)
                class_id = int(np.argmax(preds))
                class_name = CariesDetectionController.class_labels[class_id]
                confidence = float(np.max(preds))

                # Draw
                color = class_colors.get(class_name, (255, 255, 255))
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness=3)
                # label = f"{class_name} ({confidence:.2f})"
                # cv2.putText(image, label, (x1, y1 - 10),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                class_summary[class_name] += 1
                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "vertices": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                })

            # Save result
            result_path = os.path.join(temp_dir, f"result_{temp_filename}")
            cv2.imwrite(result_path, image)

            # Prepare response
            response = Response()
            response.status_code = 200
            response.headers['Content-Type'] = 'multipart/mixed; boundary=frame'
            boundary = "frame"
            boundary_bytes = f"--{boundary}\r\n".encode()
            end_boundary = f"--{boundary}--\r\n".encode()

            body = BytesIO()
            body.write(boundary_bytes)
            body.write(b"Content-Type: application/json\r\n\r\n")
            body.write(json.dumps({
                "class_summary": dict(class_summary),
                "detections": detections
            }).encode())
            body.write(b"\r\n")

            body.write(boundary_bytes)
            body.write(b"Content-Type: image/jpeg\r\n\r\n")
            with open(result_path, "rb") as f:
                body.write(f.read())
            body.write(b"\r\n")
            body.write(end_boundary)
            response.set_data(body.getvalue())

            os.remove(image_path)
            # os.remove(result_path)
            # try:
            #     os.rmdir(temp_dir)
            # except OSError:
            #     pass  
            
        
            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500


  
    
    # @staticmethod
    # def classify_efficientnet(efficientnet_model):
    #     class_labels = {
    #     0: "Caries Class 1",
    #     1: "Caries Class 2",
    #     2: "Caries Class 3",
    #     3: "Caries Class 4",
    #     4: "Caries Class 5"
    #     }
    #     if 'image' not in request.files:
    #         return jsonify({"error": "No image file provided"}), 400

    #     image_file = request.files['image']
    #     if image_file.filename == '':
    #         return jsonify({"error": "Empty filename"}), 400

    #     try:
    #         # === Save Temp Image === #
    #         project_root = current_app.root_path
    #         temp_dir = os.path.join(project_root, "temp_uploads")
    #         os.makedirs(temp_dir, exist_ok=True)

    #         temp_filename = f"{uuid.uuid4().hex}.jpg"
    #         image_path = os.path.join(temp_dir, temp_filename)
    #         image_file.save(image_path)

    #         # === Load Model === #
    #         model_path = os.path.join(project_root, "models", efficientnet_model)
    #         if not os.path.exists(model_path):
    #             raise FileNotFoundError(f"Model not found at {model_path}")
            
    #         model = load_model(model_path)

    #         # === Preprocess Image === #
    #         image = Image.open(image_path).convert("RGB")
    #         image = image.resize((224, 224))
    #         image = img_to_array(image)
    #         image = preprocess_input(image)
    #         image = np.expand_dims(image, axis=0)

    #         # === Predict === #
    #         predictions = model.predict(image)
    #         class_id = int(np.argmax(predictions))
    #         confidence = float(np.max(predictions))
    #         class_name = class_labels.get(class_id, f"Class {class_id}")

    #         os.remove(image_path)

    #         try:
    #             os.rmdir(temp_dir)
    #         except OSError:
    #             pass  
                
    #         return jsonify({
    #             "predicted_class_id": class_id,
    #             "predicted_class_name": class_name,
    #             "confidence": round(confidence, 4)
    #         })

    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500


   
    @staticmethod
    def _classify_YOLO_NAS():
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        try:
            project_root = current_app.root_path
            temp_dir = os.path.join(project_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)

            temp_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(temp_dir, temp_filename)
            image_file.save(image_path)

            image = cv2.imread(image_path)

            # Send image to Roboflow API
            with open(image_path, "rb") as f:
                response = requests.post(
                    f"{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
                     files={"file": open(image_path, "rb")}
                )
            os.remove(image_path)

            if response.status_code != 200:
                return jsonify({"error": "Roboflow inference failed", "details": response.text}), 500

            predictions = response.json().get("predictions", [])

            # Build list of raw boxes
            boxes_raw = []
            for pred in predictions:
                class_name = pred["class"]
                confidence = pred["confidence"]
                x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]

                x1 = int(x - w / 2)
                y1 = int(y - h / 2)
                x2 = int(x + w / 2)
                y2 = int(y + h / 2)
                area = (x2 - x1) * (y2 - y1)

                boxes_raw.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "x1": x1, "y1": y1,
                    "x2": x2, "y2": y2,
                    "area": area
                })

            # Filter out smaller boxes inside larger ones
            filtered_boxes = []
            for i, boxA in enumerate(boxes_raw):
                is_inside = False
                for j, boxB in enumerate(boxes_raw):
                    if i == j:
                        continue
                    if (
                        boxA["x1"] >= boxB["x1"] and boxA["y1"] >= boxB["y1"] and
                        boxA["x2"] <= boxB["x2"] and boxA["y2"] <= boxB["y2"] and
                        boxA["area"] < boxB["area"]
                    ):
                        is_inside = True
                        break
                if not is_inside:
                    filtered_boxes.append(boxA)

            # Draw boxes and build class summary
            class_summary = defaultdict(int)
        
            class_colors = {
                "Caries Class 1": (32, 228, 26),   # green
                "Caries Class 2": (248, 170, 1),   # blue
                "Caries Class 3": (234, 0, 255),  # GBR = Yellow ✅
                "Caries Class 4":  (34, 87, 255),  # orange
                "Caries Class 5": (12, 27, 233),   # red
            }


            for box in filtered_boxes:
                class_name = box["class_name"]
                class_summary[class_name] += 1
                color = class_colors.get(class_name, (255, 255, 255))
                cv2.rectangle(image, (box["x1"], box["y1"]), (box["x2"], box["y2"]), color, thickness=4)

            result_path = os.path.join(temp_dir, f"result_{temp_filename}")
            cv2.imwrite(result_path, image)

            with open(result_path, "rb") as f:
                image_content = f.read()
            os.remove(result_path)
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

            # Create multipart response
            response = Response()
            response.status_code = 200
            response.headers['Content-Type'] = 'multipart/mixed; boundary=frame'

            boundary = "frame"
            boundary_bytes = f"--{boundary}\r\n".encode()
            end_boundary = f"--{boundary}--\r\n".encode()
            body = BytesIO()

            body.write(boundary_bytes)
            body.write(b"Content-Type: application/json\r\n\r\n")
            body.write(json.dumps({"class_summary": dict(class_summary)}).encode())
            body.write(b"\r\n")

            body.write(boundary_bytes)
            body.write(b"Content-Type: image/jpeg\r\n\r\n")
            body.write(image_content)
            body.write(b"\r\n")

            body.write(end_boundary)
            response.set_data(body.getvalue())

            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    
    @staticmethod
    def _classify_YOLOv8(model_filename):
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        try:
            project_root = current_app.root_path
            temp_dir = os.path.join(project_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)

            temp_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(temp_dir, temp_filename)
            image_file.save(image_path)

            model_path = os.path.join(project_root, "models", model_filename)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found at {model_path}")

            model = YOLO(model_path)
            results = model(image_path)

            image = cv2.imread(image_path)
            os.remove(image_path)

            class_summary = defaultdict(int)
           
          
            class_colors = {
                "Caries Class 1": (32, 228, 26),   # green
                "Caries Class 2": (248, 170, 1),   # blue
                "Caries Class 3": (234, 0, 255),  # GBR = Yellow ✅
                "Caries Class 4":  (34, 87, 255),  # orange
                "Caries Class 5": (12, 27, 233),   # red
            }




            boxes_raw = []
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_name = results[0].names[class_id]
                area = (x2 - x1) * (y2 - y1)

                boxes_raw.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "area": area
                })

            filtered_boxes = []
            for i, boxA in enumerate(boxes_raw):
                is_inside = False
                for j, boxB in enumerate(boxes_raw):
                    if i == j:
                        continue
                    if (
                        boxA["x1"] >= boxB["x1"] and boxA["y1"] >= boxB["y1"] and
                        boxA["x2"] <= boxB["x2"] and boxA["y2"] <= boxB["y2"] and
                        boxA["area"] < boxB["area"]
                    ):
                        is_inside = True
                        break
                if not is_inside:
                    filtered_boxes.append(boxA)

            for box in filtered_boxes:
                class_id = box["class_id"]
                class_name = box["class_name"]
                x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]

                class_summary[class_name] += 1

                color = class_colors.get(class_name, (255, 255, 255))  # default white

                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness=4)

            # Save final image
            result_path = os.path.join(temp_dir, f"result_{temp_filename}")
            cv2.imwrite(result_path, image)

            # Instead of base64, send image directly
            response_json = jsonify({"class_summary": dict(class_summary)})
            # image_file = open(result_path, "rb")

            with open(result_path, "rb") as f:
                image_content = f.read()
            os.remove(result_path)

            try:
                os.rmdir(temp_dir)
            except OSError:
                pass  # Folder not empty or other issue, so skip deletion
            
        
            response = Response()
            response.status_code = 200
            response.headers['Content-Type'] = 'multipart/mixed; boundary=frame'

            # Construct multipart body manually
            boundary = "frame"
            boundary_bytes = f"--{boundary}\r\n".encode()
            end_boundary = f"--{boundary}--\r\n".encode()

            body = BytesIO()

            # Part 1: JSON summary
            body.write(boundary_bytes)
            body.write(b"Content-Type: application/json\r\n\r\n")
            body.write(json.dumps({"class_summary": dict(class_summary)}).encode())
            body.write(b"\r\n")

            # Part 2: Image
            body.write(boundary_bytes)
            body.write(b"Content-Type: image/jpeg\r\n\r\n")
            body.write(image_content)
            body.write(b"\r\n")

            body.write(end_boundary)
            response.set_data(body.getvalue())

            return response

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

    @staticmethod
    def _classify_YOLOv8_vertices():
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        try:
            project_root = current_app.root_path
            temp_dir = os.path.join(project_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)

            temp_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(temp_dir, temp_filename)
            image_file.save(image_path)

            model_path = os.path.join(project_root, "models", "yolov8m_100epochs.pt")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model not found at {model_path}")

            model = YOLO(model_path)
            results = model(image_path)

            os.remove(image_path)
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

            boxes_raw = []
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_name = results[0].names[class_id]
                area = (x2 - x1) * (y2 - y1)

                boxes_raw.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                    "area": area
                })

            filtered_boxes = []
            for i, boxA in enumerate(boxes_raw):
                is_inside = False
                for j, boxB in enumerate(boxes_raw):
                    if i == j:
                        continue
                    if (
                        boxA["x1"] >= boxB["x1"] and boxA["y1"] >= boxB["y1"] and
                        boxA["x2"] <= boxB["x2"] and boxA["y2"] <= boxB["y2"] and
                        boxA["area"] < boxB["area"]
                    ):
                        is_inside = True
                        break
                if not is_inside:
                    filtered_boxes.append(boxA)

            class_summary = defaultdict(int)
            output_boxes = []
            for box in filtered_boxes:
                class_name = box["class_name"]
                class_summary[class_name] += 1

                output_boxes.append({
                    "class_name": class_name,
                    "confidence": round(box["confidence"], 3),
                    "vertices": {
                        "x1": box["x1"],
                        "y1": box["y1"],
                        "x2": box["x2"],
                        "y2": box["y2"]
                    },
                })

            return jsonify({
                "class_summary": dict(class_summary),
                "detections": output_boxes
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

    @staticmethod
    def _classify_YOLO_NAS_vertices():
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        try:
            project_root = current_app.root_path
            temp_dir = os.path.join(project_root, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)

            temp_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(temp_dir, temp_filename)
            image_file.save(image_path)

            # Send image to Roboflow API
            with open(image_path, "rb") as f:
                response = requests.post(
                    f"{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
                    files={"file": f}
                )

            os.remove(image_path)
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

            if response.status_code != 200:
                return jsonify({"error": "Roboflow inference failed", "details": response.text}), 500

            predictions = response.json().get("predictions", [])

            # Extract raw boxes
            boxes_raw = []
            for pred in predictions:
                class_name = pred["class"]
                confidence = pred["confidence"]
                x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]

                x1 = int(x - w / 2)
                y1 = int(y - h / 2)
                x2 = int(x + w / 2)
                y2 = int(y + h / 2)
                area = (x2 - x1) * (y2 - y1)

                boxes_raw.append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "x1": x1, "y1": y1,
                    "x2": x2, "y2": y2,
                    "area": area
                })

            # Filter out smaller boxes inside larger ones
            filtered_boxes = []
            for i, boxA in enumerate(boxes_raw):
                is_inside = False
                for j, boxB in enumerate(boxes_raw):
                    if i == j:
                        continue
                    if (
                        boxA["x1"] >= boxB["x1"] and boxA["y1"] >= boxB["y1"] and
                        boxA["x2"] <= boxB["x2"] and boxA["y2"] <= boxB["y2"] and
                        boxA["area"] < boxB["area"]
                    ):
                        is_inside = True
                        break
                if not is_inside:
                    filtered_boxes.append(boxA)

            # Format output
            class_summary = defaultdict(int)
            output_boxes = []
            for box in filtered_boxes:
                class_name = box["class_name"]
                class_summary[class_name] += 1

                output_boxes.append({
                    "class_name": class_name,
                    "confidence": round(box["confidence"], 3),
                    "vertices": {
                        "x1": box["x1"],
                        "y1": box["y1"],
                        "x2": box["x2"],
                        "y2": box["y2"]
                    }
                })

            return jsonify({
                "class_summary": dict(class_summary),
                "detections": output_boxes
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500



    