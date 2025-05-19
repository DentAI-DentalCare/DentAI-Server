from flask import request, jsonify
from models import db
from flask_jwt_extended import get_jwt_identity
from models.user import User
from werkzeug.utils import secure_filename
from models.doctor import Doctor
from models.user_image import UserImage
from middlewares.image_base64 import image_to_base64_middleware
import os
import cloudinary.uploader
from urllib.parse import unquote


class UserController:

    @staticmethod
    def get_profile():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = user.to_dict()
        return jsonify(user_data), 200

    @staticmethod
    def update_profile():
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        print(f"Data received for update: {data}")

        # Check if new email is provided and it's different from the current one
        new_email = data.get("email")
        if new_email and new_email != user.email:
            existing_email_user = User.query.filter_by(email=new_email).first()
            if existing_email_user:
                return jsonify({"error": "Email already in use"}), 400
            user.email = new_email

        # Check if new phone number is provided and it's different from current one
        new_phone = data.get("phone_number")
        if new_phone and new_phone != user.phone_number:
            existing_phone_user = User.query.filter_by(phone_number=new_phone).first()
            if existing_phone_user:
                return jsonify({"error": "Phone number already in use"}), 400
            user.phone_number = new_phone

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.birth_date = data.get("birth_date", user.birth_date)
        user.gender = data.get("gender", user.gender)

        if user.role.value.lower() == "doctor":
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            if doctor:
                doctor.specialization = data.get("specialization", doctor.specialization)
                doctor.bio = data.get("bio", doctor.bio)
                doctor.consultation_fee = data.get("consultation_fee", doctor.consultation_fee)
                doctor.experience_years = data.get("experience_years", doctor.experience_years)

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200


    @staticmethod
    def delete_account():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User account deleted successfully"}), 200

    @staticmethod
    def upload_profile_image():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if 'image' not in request.files:
            return jsonify({"error": "No Image attached"}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "No selected image"}), 400

        if file:
            if user.profile_picture_url:
                public_id = '/'.join(user.profile_picture_url.split('/')[-3:]).split('.')[0]
                cloudinary.uploader.destroy(public_id)

            upload_result = cloudinary.uploader.upload(
                file,
                folder=f"{user.email}/profile"
            )
            image_url = upload_result['secure_url']

            user.profile_picture_url = image_url
            db.session.commit()

            return jsonify({"message": "Profile picture uploaded successfully", "url": image_url}), 201

    @staticmethod
    def delete_profile_image():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user.profile_picture_url:
            return jsonify({"error": "No profile picture to delete"}), 400

        public_id_encoded = '/'.join(user.profile_picture_url.split('/')[7:]).rsplit('.', 1)[0]
        public_id = unquote(public_id_encoded)
        print(f"Public ID: {public_id}")

        result = cloudinary.uploader.destroy(public_id)

        if result.get('result') != 'ok':
            return jsonify({"error": "Cloudinary deletion failed", "details": result}), 500

        user.profile_picture_url = None
        db.session.commit()

        return jsonify({"message": "Profile picture deleted successfully"}), 200

    @staticmethod
    def get_user_images():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        images = UserImage.query.filter_by(user_id=user.user_id).all()

        image_list = []
        for image in images:
            if "/teeth/" in image.image_url:
                image_list.append({
                    "id": image.image_id,
                    "uploaded_at": image.uploaded_at.isoformat(),
                    "url": image.image_url
                })

        return jsonify({"images": image_list}), 200

    @staticmethod
    def get_image_by_id(image_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        image = UserImage.query.filter_by(image_id=image_id, user_id=user.user_id).first()
        if not image:
            return jsonify({"error": "Not found"}), 404

        return jsonify({
            "id": image.image_id,
            "uploaded_at": image.uploaded_at.isoformat(),
            "image_url": image.image_url
        }), 200
