import base64
from flask import request, jsonify
from io import BytesIO

def image_to_base64_middleware():
    """
    Middleware that converts an uploaded image (from form-data) to base64 and attaches it to request.
    Looks for key 'image' in files.
    """
    if request.method in ['POST', 'PUT'] and request.content_type and 'multipart/form-data' in request.content_type:
        if 'image' not in request.files:
            return jsonify({"error": "Image file is missing in form-data"}), 400

        image_file = request.files['image']
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        request.image_base64 = image_base64  # attach to request
        

def base64_to_image_middleware():
    """
    Middleware that decodes a base64 string from JSON body and attaches BytesIO image to request.
    Looks for key 'image_base64' in JSON body.
    """
    if request.method in ['POST', 'PUT'] and request.is_json:
        data = request.get_json()
        base64_str = data.get('image_base64')
        if not base64_str:
            return jsonify({"error": "Missing 'image_base64' in JSON body"}), 400

        try:
            image_bytes = base64.b64decode(base64_str)
            request.decoded_image = BytesIO(image_bytes)  # attach BytesIO stream to request
        except Exception as e:
            return jsonify({"error": "Failed to decode base64 image", "details": str(e)}), 400
