from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
from . import db  # assuming this is your initialized SQLAlchemy instance

class UserImage(db.Model):
    __tablename__ = "user_images"

    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(512), nullable=False)
    diagnosis = db.Column(JSON)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
