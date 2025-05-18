from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import enum
from sqlalchemy.dialects.mysql import LONGTEXT
from . import db

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"

class RoleEnum(enum.Enum):
    Patient = "Patient"
    Doctor = "Doctor"

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    national_id = db.Column(db.BigInteger, unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)  # ✅ updated to string
    address = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.Patient)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture_url = db.Column(db.String(512), nullable=True)  # ✅ renamed for consistency
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum(GenderEnum), nullable=True)

    def to_dict(self):
        data = {
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "national_id": self.national_id,
            "address": self.address,
            "role": self.role.name,
            "profile_picture_url": self.profile_picture_url,
            "birth_date": self.birth_date,
            "created_at": self.created_at,
            "gender": self.gender.name if self.gender else None,
        }

        # Merge doctor profile if exists
        if self.role.name.lower() == "doctor" and hasattr(self, "doctor_profile"):
            data.update({
                "specialization": self.doctor_profile.specialization,
                "bio": self.doctor_profile.bio,
                "experience_years": self.doctor_profile.experience_years,
                "average_rating": self.doctor_profile.average_rating,
                "consultation_fee": self.doctor_profile.consultation_fee,
                "title": self.doctor_profile.title.value,
            })

        return data
