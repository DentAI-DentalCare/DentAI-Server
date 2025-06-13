from flask_mongoengine import MongoEngine
from datetime import datetime
import enum

db = MongoEngine()


# ─── Enums ─────────────────────────────────────────────────────────────

class GenderEnum(enum.Enum):
    male   = "male"
    female = "female"

class RoleEnum(enum.Enum):
    Patient = "Patient"
    Doctor  = "Doctor"

class TitleEnum(enum.Enum):
    Lecturer   = "Lecturer"
    Professor  = "Professor"
    Consultant = "Consultant"
    Specialist = "Specialist"
    Dentist    = "Dentist"

class DayEnum(enum.Enum):
    Monday    = "Monday"
    Tuesday   = "Tuesday"
    Wednesday = "Wednesday"
    Thursday  = "Thursday"
    Friday    = "Friday"
    Saturday  = "Saturday"
    Sunday    = "Sunday"

class StatusEnum(enum.Enum):
    Scheduled = "Scheduled"
    Completed = "Completed"
    Cancelled = "Cancelled"


# ─── Documents ────────────────────────────────────────────────────────

class User(db.Document):
    meta = {"collection": "users"}
    first_name          = db.StringField(required=True, max_length=255)
    last_name           = db.StringField(required=True, max_length=255)
    national_id         = db.LongField(required=False, unique=True)
    phone_number        = db.StringField(required=False, max_length=20, unique=True)
    address             = db.StringField(max_length=255)
    email               = db.EmailField(required=True, unique=True)
    password            = db.StringField(required=True)
    role                = db.EnumField(RoleEnum, default=RoleEnum.Patient)
    created_at          = db.DateTimeField(default=datetime.utcnow)
    profile_picture_url = db.StringField(max_length=512)
    birth_date          = db.DateField()
    gender              = db.EnumField(GenderEnum)

    def to_dict(self):
        # base user data
        data = {
            "user_id":             str(self.id),
            "first_name":          self.first_name,
            "last_name":           self.last_name,
            "email":               self.email,
            "national_id":         self.national_id,
            "phone_number":        self.phone_number,
            "address":             self.address,
            "role":                self.role.name,
            "profile_picture_url": self.profile_picture_url,
            "birth_date":          self.birth_date.isoformat() if self.birth_date else None,
            "created_at":          self.created_at.isoformat(),
            "gender":              self.gender.name if self.gender else None,
        }

        doctor = Doctor.objects(user=self).first()
        if doctor:
            data.update({
                "specialization":    doctor.specialization,
                "clinic_address":    doctor.clinic_address,
                "bio":               doctor.bio,
                "experience_years":  doctor.experience_years,
                "average_rating":    doctor.average_rating,
                "consultation_fee":  doctor.consultation_fee,
                "title":             doctor.title.name,
            })

        return data

class Doctor(db.Document):
    meta = {"collection": "doctors"}
    user                = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    specialization      = db.StringField(max_length=255)
    title               = db.EnumField(TitleEnum, default=TitleEnum.Dentist)
    bio                 = db.StringField()
    clinic_address      = db.StringField(max_length=255)
    experience_years    = db.IntField()
    consultation_fee    = db.IntField(required=True)
    average_rating      = db.FloatField(default=0.0)


class UserInsurance(db.Document):
    meta = {"collection": "user_insurances"}
    user           = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    company_name   = db.StringField(required=True, max_length=255)
    insurance_number = db.StringField(required=True, max_length=255)
    expiry_date    = db.DateField(required=True)
    card_image_url = db.URLField(required=True, max_length=512)
    created_at     = db.DateTimeField(default=datetime.utcnow)


class UserImage(db.Document):
    meta = {"collection": "user_images"}
    user        = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    image_url   = db.URLField(required=True, max_length=512)
    diagnosis   = db.DictField()   # stores your JSON blob
    uploaded_at = db.DateTimeField(default=datetime.utcnow)


class ConsultationThread(db.Document):
    meta = {"collection": "consultation_threads"}
    image      = db.ReferenceField(UserImage, null=True)
    patient    = db.ReferenceField(User,      required=True, reverse_delete_rule=db.CASCADE)
    doctor     = db.ReferenceField(Doctor,    required=True, reverse_delete_rule=db.CASCADE)
    created_at = db.DateTimeField(default=datetime.utcnow)

class ConsultationMessage(db.Document):
    meta = {"collection": "consultation_messages"}
    thread      = db.ReferenceField(
                     ConsultationThread,
                     required=True,
                     reverse_delete_rule=db.CASCADE
                  )
    sender_role = db.EnumField(RoleEnum, required=True)
    message     = db.StringField()
    image_url   = db.URLField(max_length=512)
    sent_at     = db.DateTimeField(default=datetime.utcnow)


class TimeSlot(db.Document):
    meta = {"collection": "time_slots"}
    doctor         = db.ReferenceField(Doctor, reverse_delete_rule=db.CASCADE)
    available_day  = db.EnumField(DayEnum, required=True)
    available_date = db.DateField(required=True)
    start_time     = db.StringField(required=True)  # e.g. "09:00:00"
    end_time       = db.StringField(required=True)  # e.g. "17:00:00"


class Appointment(db.Document):
    meta = {"collection": "appointments"}
    patient         = db.ReferenceField(User,   required=True)
    doctor          = db.ReferenceField(Doctor, required=True)
    appointment_date= db.DateField(required=True)
    start_time      = db.StringField(required=True)
    end_time        = db.StringField(required=True)
    status          = db.EnumField(StatusEnum, default=StatusEnum.Scheduled)
    notes           = db.StringField()
    diagnosis       = db.StringField()
    treatment_plan  = db.StringField()
    created_at      = db.DateTimeField(default=datetime.utcnow)
