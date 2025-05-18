from flask import Blueprint, request, jsonify
from controllers.ocr_controller import analyze_id_controller
from werkzeug.utils import secure_filename
import tempfile
import os

ocr_blueprint = Blueprint('ocr', __name__)

@ocr_blueprint.route('/analyze-id', methods=['POST'])
def analyze_id():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)

    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp:
        file.save(temp.name)
        temp_path = temp.name

    result = analyze_id_controller(temp_path, filename)

    # Optional: cleanup temp file after processing
    os.remove(temp_path)

    return jsonify(result), 200
