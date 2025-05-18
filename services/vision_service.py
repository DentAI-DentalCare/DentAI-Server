from PIL import Image
import cv2
import os
import io
import numpy as np
from google.cloud import vision
import arabic_reshaper
from bidi.algorithm import get_display
from services.llm_service import get_national_id_info
from dotenv import load_dotenv


load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
def preprocess_image(image_path, output_path="preprocessed_image.jpg", padding=50, background_color=(255, 255, 255)):
    image = Image.open(image_path)
    new_width = image.width + 2 * padding
    new_height = image.height + 2 * padding
    canvas = Image.new("RGB", (new_width, new_height), background_color)
    canvas.paste(image, (padding, padding))
    canvas.save(output_path)

    image = cv2.imread(output_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    norm = np.zeros_like(gray)
    norm = cv2.normalize(gray, norm, 0, 255, cv2.NORM_MINMAX)
    denoise = cv2.fastNlMeansDenoising(norm, None, 7)
    sharpen = cv2.filter2D(denoise, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
    cv2.imwrite(output_path, sharpen)
    return output_path if os.path.getsize(output_path) < 20 * 1024 * 1024 else None

def detect_text(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description.strip() if response.text_annotations else ""

def process_image(image_path, file_name):
    processed_path = preprocess_image(image_path)
    image_to_use = processed_path if processed_path else image_path

    text = detect_text(image_to_use)
    if not text:
        return {"national_id_info": {"error": "No text detected", "fileName": file_name}}

    national_id_info = get_national_id_info(text)

    if "error" in national_id_info and national_id_info["error"] == "National ID is incorrect":
        text = detect_text(image_path)
        national_id_info = get_national_id_info(text)

    national_id_info["fileName"] = file_name
    return {"national_id_info": national_id_info}
