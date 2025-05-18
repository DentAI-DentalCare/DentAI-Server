from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import enum
from sqlalchemy.dialects.mysql import LONGTEXT 
from models.user import User  # make sure the path is correct
from . import db

class TitleEnum(enum.Enum):
    Lecturer = "Lecturer"
    Professor = "Professor"
    Consultant = "Consultant"
    Specialist = "Specialist"
    Dentist = "Dentist"

class Doctor(db.Model):
    __tablename__ = "doctors"

    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    specialization = db.Column(db.String(255))    
    title = db.Column(db.Enum(TitleEnum), default=TitleEnum.Dentist)
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Integer, nullable=False)
    average_rating = db.Column(db.Float, default=0)

    user = db.relationship(User, backref=db.backref("doctor_profile", uselist=False))
