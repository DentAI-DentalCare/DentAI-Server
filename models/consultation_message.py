from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db  # or from models import db
import enum

class SenderRoleEnum(enum.Enum):
    Patient = "Patient"
    Doctor = "Doctor"


class ConsultationMessage(db.Model):
    __tablename__ = "consultation_messages"

    message_id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("consultation_threads.thread_id"), nullable=False)
    sender_role = db.Column(db.Enum(SenderRoleEnum), nullable=False)
    message = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(512), nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    thread = db.relationship("ConsultationThread", backref="messages")
