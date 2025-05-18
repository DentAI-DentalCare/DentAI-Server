from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import enum
from sqlalchemy.dialects.mysql import LONGTEXT
from . import db  # or from models import db if you're outside the models folder
from sqlalchemy import Enum as SQLAlchemyEnum

# ✅ Step 1: Define a proper Python Enum
class AppointmentStatusEnum(enum.Enum):
    Scheduled = "Scheduled"
    Completed = "Completed"
    Cancelled = "Cancelled"

# ✅ Step 2: Use SQLAlchemy Enum with the defined Python Enum
class Appointment(db.Model):
    __tablename__ = "appointments"

    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(SQLAlchemyEnum(AppointmentStatusEnum), default=AppointmentStatusEnum.Scheduled, nullable=False)
    notes = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", backref="appointments")
    doctor = db.relationship("Doctor", backref="appointments")
