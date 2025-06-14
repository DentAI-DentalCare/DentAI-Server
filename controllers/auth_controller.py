# controllers/auth_controller.py
import smtplib, random, string, os
from email.message import EmailMessage
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity
from model import (
    db,
    User,
    Doctor,
    RoleEnum,
    TitleEnum,
    GenderEnum
)
from services.email_service import send_styled_email

# temporary in-memory store for reset codes
reset_codes = []  


class AuthController:

    @staticmethod
    def signup():
        data = request.get_json() or {}

        # grab incoming fields
        first_name       = data.get("first_name")
        last_name        = data.get("last_name")
        email            = data.get("email")
        password         = data.get("password")
        national_id      = data.get("national_id")
        phone_number     = data.get("phone_number")
        address          = data.get("address")
        birth_date       = data.get("birth_date")      # e.g. "2025-06-13"
        gender_str       = data.get("gender", "").lower()
        role_str         = data.get("role", "").capitalize()

        # doctor-only fields
        specialization   = data.get("specialization")
        bio              = data.get("bio")
        experience_years = data.get("experience_years")
        title_str        = data.get("title")
        consultation_fee = data.get("consultation_fee")

        # basic validation
        if not all([first_name, last_name, email, password,
                     gender_str, role_str]):
            return jsonify({
                "error": "first_name, last_name, email, password, "
                         "phone_number, gender, and role are required"
            }), 400

        # uniqueness checks
        if User.objects(national_id=national_id).first():
            return jsonify({"error": "National ID already exists"}), 400
        if User.objects(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
        if User.objects(phone_number=phone_number).first():
            return jsonify({"error": "Phone number already exists"}), 400
        
        
        print(f"Received signup request: {data}")

        # prepare enums
        try:
            gender_enum = GenderEnum(gender_str)
        except ValueError:
            return jsonify({"error": "Invalid gender"}), 400

        try:
            role_enum = RoleEnum(role_str)
        except ValueError:
            return jsonify({"error": "Invalid role"}), 400

        # hash password
        hashed_pw = generate_password_hash(password)

        # create user document
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pw,
            national_id=national_id,
            phone_number=phone_number,
            address=address,
            birth_date=birth_date,
            gender=gender_enum,
            role=role_enum,
            created_at=datetime.utcnow()
        )
        user.save()

        # if doctor, also create a Doctor doc
        if role_enum is RoleEnum.Doctor:
            # validate required doctor fields
            if not all([specialization, bio, experience_years, title_str, consultation_fee]):
                return jsonify({
                    "error": "specialization, bio, experience_years, title and consultation_fee are required for doctors"
                }), 400

            try:
                title_enum = TitleEnum(title_str)
            except ValueError:
                return jsonify({"error": "Invalid title"}), 400

            doctor = Doctor(
                user=user,
                specialization=specialization,
                bio=bio,
                experience_years=experience_years,
                title=title_enum,
                consultation_fee=consultation_fee,
                average_rating=0.0
            )
            doctor.save()

        return jsonify({"message": "User registered successfully"}), 201


    @staticmethod
    def login():
        data = request.get_json() or {}
        email    = data.get("email")
        password = data.get("password")

        print(f"Received login request: {data}")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        print(f"Received login request: {data}")

        user = User.objects(email=email).first()
        print(f"User found: {user.password if user else 'None'}")
        print(f"Password provided: {user}")
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        print(f"Received login request: {data}")

        # build JWT
        access_token = create_access_token(
            identity=user.email,
            additional_claims={
                "email": user.email,
                "role": user.role.value
            },
            expires_delta=timedelta(days=365)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    @staticmethod
    def logout():
        return jsonify({"message": "Logout successful"}), 200

    @staticmethod
    def send_reset_code():
        data = request.get_json() or {}
        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        user = User.objects(email=email).first()
        if not user:
            return jsonify({"error": "Email not registered"}), 404

        # generate 6-digit numeric code
        code = "".join(random.choices(string.digits, k=6))

        try:
            send_styled_email(email, code)
        except Exception as e:
            return jsonify({
                "error":   "Failed to send email",
                "details": str(e)
            }), 500

        # store for later verification
        reset_codes.append({"email": email, "code": code})
        return jsonify({"message": "Reset code sent to email"}), 200


    @staticmethod
    def verify_reset_code():
        data  = request.get_json() or {}
        email = data.get("email")
        code  = data.get("code")
        if not email or not code:
            return jsonify({"error": "Email and code are required"}), 400

        match = next(
            (item for item in reset_codes
             if item["email"] == email and item["code"] == code),
            None
        )
        if not match:
            return jsonify({"error": "Invalid code or email"}), 400

        user = User.objects(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # consume the code
        reset_codes.remove(match)
        return jsonify({"message": "Code verified successfully"}), 200


    @staticmethod
    def reset_password():
        data         = request.get_json() or {}
        email        = data.get("email")
        new_password = data.get("new_password")
        if not all([email, new_password]):
            return jsonify({
                "error": "Email and new password are required"
            }), 400

        user = User.objects(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # update & save
        user.password = generate_password_hash(new_password)
        user.save()

        return jsonify({"message": "Password reset successfully"}), 200


    @staticmethod
    def change_password():
        data         = request.get_json() or {}
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        if not all([old_password, new_password]):
            return jsonify({
                "error": "Old and new passwords are required"
            }), 400

        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user or not check_password_hash(user.password, old_password):
            return jsonify({"error": "Old password is incorrect"}), 400

        # update & save
        user.password = generate_password_hash(new_password)
        user.save()

        return jsonify({"message": "Password changed successfully"}), 200