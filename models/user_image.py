from sqlalchemy.dialects.mysql import LONGTEXT  # 👈 required import
from datetime import datetime # assuming you’re using the same db instance
from . import db  # or from models import db if you're outside the models folder

class UserImage(db.Model):
    __tablename__ = "user_images"

    image_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(512), nullable=False)  # 👈 use LONGTEXT here
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
