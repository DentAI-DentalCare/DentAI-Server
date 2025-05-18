from sqlalchemy.dialects.mysql import LONGTEXT  # 👈 required import
from datetime import datetime # assuming you’re using the same db instance
from . import db  # or from models import db if you're outside the models folder


class UserInsurance(db.Model):
    __tablename__ = 'user_insurances'

    insurance_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    insurance_number = db.Column(db.String(255), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    card_image_url = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
