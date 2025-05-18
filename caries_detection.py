from inference_sdk import InferenceHTTPClient
import requests

# Initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="uogO0X9KTYvheyifKHL6"
)

# Run inference
result = CLIENT.infer("46.jpg", model_id="DentAI2-4vtbx/1")

# Print full API response to check available keys
print("API Response:", result)
