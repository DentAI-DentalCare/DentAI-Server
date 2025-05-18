from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db  # or from models import db


class ConsultationThread(db.Model):
    __tablename__ = "consultation_threads"

    thread_id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("user_images.image_id"), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    image = db.relationship("UserImage", backref="consultation_threads")
    patient = db.relationship("User", backref="consultation_threads", foreign_keys=[patient_id])
    doctor = db.relationship("Doctor", backref="consultation_threads")
