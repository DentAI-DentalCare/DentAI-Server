from services.vision_service import process_image

def analyze_id_controller(image_path, filename):
    return process_image(image_path, filename)
