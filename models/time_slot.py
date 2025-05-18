from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import enum
from sqlalchemy.dialects.mysql import LONGTEXT 
from . import db  # or from models import db if you're outside the models folder


class DayOfWeekEnum(enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"

class TimeSlot(db.Model):
    __tablename__ = "time_slots"

    slot_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    available_day = db.Column(db.Enum(DayOfWeekEnum), nullable=False)
    available_date = db.Column(db.Date, nullable=False) 
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    doctor = db.relationship("Doctor", backref="time_slots")
