import smtplib, random, string, os
from models import db
from email.message import EmailMessage
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
from models.user import User
from models.doctor import Doctor
from services.email_service import send_styled_email

reset_codes = []  # Temporary in-memory store (replace with Redis or DB in production)

class AuthController:

    @staticmethod
    def signup():
        data = request.json
        print(data)
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        password = data.get("password")
        email = data.get("email")
        national_id = data.get("national_id")
        address = data.get("address")
        gender = data.get("gender", "").lower()
        birth_date = data.get("birth_date")
        phone_number = data.get("phone_number")
        consultation_fee = data.get("consultation_fee")
        bio = data.get("bio")
        experience_years = data.get("experience_years") 
        specialization = data.get("specialization") 
        title = data.get("title") 
        role = data.get("role").capitalize()

        if not first_name or not last_name or not password or not birth_date or not email or not national_id or not gender or not role:
            return jsonify({"error": "First Name, Last Name, National ID, gender, email, role, and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        hashed_password = generate_password_hash(password)

        # Create the user record
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            national_id=national_id,
            address=address,
            phone_number=phone_number,
            gender=gender,
            birth_date=birth_date,
            role=role,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
         
        # If Doctor, create a Doctor profile with extra fields
        if role.lower() == "doctor":
            doctor = Doctor(
                user_id=user.user_id,
                bio=bio,
                specialization=specialization,
                experience_years=experience_years,
                title=title,
                consultation_fee=consultation_fee
            )
            db.session.add(doctor)
            db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    @staticmethod
    def login():
        data = request.json
        print(data)
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid email or password"}), 401

        access_token = create_access_token(
            identity=user.email,
            additional_claims={
                "email": user.email,
                "role": user.role.value
            },
            expires_delta=timedelta(days=365) 
        )

        user_data = user.to_dict()

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user_data
        }), 200

    @staticmethod
    def logout():
        return jsonify({"message": "Logout successful"}), 200

    @staticmethod
    def send_reset_code():
        data = request.json
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Email not registered"}), 404

        code = ''.join(random.choices(string.digits, k=6))

        try:
            send_styled_email(email, code)
        except Exception as e:
            return jsonify({"error": "Failed to send email", "details": str(e)}), 500

        reset_codes.append({"email": email, "code": code})

        return jsonify({"message": "Reset code sent to email"}), 200

    @staticmethod
    def verify_reset_code():
        data = request.json
        email = data.get("email")
        code = data.get("code")

        if not email or not code:
            return jsonify({"error": "Email and code are required"}), 400

        match = next((item for item in reset_codes if item["email"] == email and item["code"] == code), None)
        if not match:
            return jsonify({"error": "Invalid code or email"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        reset_codes.remove(match)

        return jsonify({"message": "Code verified successfully"}), 200

    @staticmethod
    def reset_password():
        data = request.json
        email = data.get("email")
        new_password = data.get("new_password")

        if not all([email, new_password]):
            return jsonify({"error": "Email and new password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"message": "Password reset successfully"}), 200

    @staticmethod
    def change_password():
        data = request.json
        current_user = get_jwt_identity()
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not all([old_password, new_password]):
            return jsonify({"error": "Old and new passwords are required"}), 400

        user = User.query.filter_by(email=current_user).first()
        if not user or not check_password_hash(user.password, old_password):
            return jsonify({"error": "Old password is incorrect"}), 400

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"message": "Password changed successfully"}), 200
