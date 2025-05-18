from flask import Flask
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config import Config
from middlewares.auth_middleware import verify_token
import cloudinary
from config import Config
from routes.auth import auth_blueprint
from routes.user import user_blueprint
from routes.caries_detection import caries_detection_blueprint
from routes.doctor import doctor_blueprint
from routes.appointment import appointment_blueprint
from routes.appointment import appointment_blueprint
from routes.dummy_data import dummy_blueprint
from routes.consultation import consultation_blueprint
from routes.insurance import insurance_blueprint
from routes.ocr import ocr_blueprint
from models.user import db  # ✅ this line is key

app = Flask(__name__)
app.config.from_object(Config)

# ✅ Init SQLAlchemy with app
db.init_app(app)

# Create tables (only in dev)
with app.app_context():
    db.create_all()

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)



# JWT Config
app.config["JWT_SECRET_KEY"] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# Register Blueprints
# app.register_blueprint(predict_blueprint, url_prefix="/api")
app.register_blueprint(auth_blueprint, url_prefix="/api/auth")
app.register_blueprint(user_blueprint, url_prefix="/api/user")
app.register_blueprint(doctor_blueprint, url_prefix="/api/doctor")
app.register_blueprint(appointment_blueprint, url_prefix="/api/appointment")
app.register_blueprint(caries_detection_blueprint, url_prefix="/api/caries-detection")
app.register_blueprint(consultation_blueprint, url_prefix="/api/consultation")
app.register_blueprint(insurance_blueprint, url_prefix="/api/insurance")
app.register_blueprint(ocr_blueprint, url_prefix="/api/ocr")
app.register_blueprint(dummy_blueprint, url_prefix="/api")

# Global Middleware
app.before_request(verify_token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
