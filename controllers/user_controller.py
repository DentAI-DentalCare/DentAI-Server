from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from middlewares.image_base64 import image_to_base64_middleware
import os
import cloudinary.uploader
from urllib.parse import unquote
import json
from model import User, Doctor, UserImage, RoleEnum, db

class UserController:

    @staticmethod
    def get_profile():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user.to_dict()), 200


    @staticmethod
    def update_profile():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json() or {}
        # email
        new_email = data.get("email")
        if new_email and new_email != user.email:
            if User.objects(email=new_email).first():
                return jsonify({"error": "Email already in use"}), 400
            user.email = new_email

        # phone_number
        new_phone = data.get("phone_number")
        if new_phone and new_phone != user.phone_number:
            if User.objects(phone_number=new_phone).first():
                return jsonify({"error": "Phone number already in use"}), 400
            user.phone_number = new_phone

        # other basic fields
        user.first_name = data.get("first_name", user.first_name)
        user.last_name  = data.get("last_name", user.last_name)
        user.birth_date = data.get("birth_date", user.birth_date)
        user.gender     = data.get("gender", user.gender)

        # if doctor, update doctor profile
        if user.role is RoleEnum.Doctor:
            doctor = Doctor.objects(user=user).first()
            if doctor:
                doctor.specialization   = data.get("specialization", doctor.specialization)
                doctor.bio              = data.get("bio", doctor.bio)
                doctor.consultation_fee = data.get("consultation_fee", doctor.consultation_fee)
                doctor.experience_years = data.get("experience_years", doctor.experience_years)
                doctor.save()

        # save the user
        user.save()

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
    def get_teeth_images():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        images = (
            UserImage.objects(user=user)
                     .order_by('-uploaded_at')
        )

        result = [{
            "image_id":    str(img.id),
            "image_url":   img.image_url,
            "diagnosis":   img.diagnosis,
            "uploaded_at": img.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
        } for img in images]

        return jsonify(result), 200


    @staticmethod
    def upload_teeth_image():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if 'image' not in request.files or 'diagnosis' not in request.form:
            return jsonify({"error": "Image and diagnosis are required"}), 400

        file           = request.files['image']
        diagnosis_json = request.form.get('diagnosis')
        if file.filename == '':
            return jsonify({"error": "No selected image"}), 400

        try:
            diagnosis_data = json.loads(diagnosis_json)
        except Exception:
            return jsonify({"error": "Invalid diagnosis JSON"}), 400

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"{user.email}/Teeth Images"
        )
        image_url = upload_result.get('secure_url')
        if not image_url:
            return jsonify({"error": "Cloud upload failed"}), 500

        # Save to MongoDB
        new_img = UserImage(
            user=user,
            image_url=image_url,
            diagnosis=diagnosis_data
        )
        new_img.save()

        return jsonify({
            "message":   "Teeth image uploaded successfully",
            "url":       image_url,
            "diagnosis": diagnosis_data
        }), 201


    @staticmethod
    def delete_teeth_image(image_id):
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        img = UserImage.objects(id=image_id, user=user).first()
        if not img:
            return jsonify({"error": "Image not found"}), 404

        # Derive public_id from URL for Cloudinary deletion
        try:
            parts     = img.image_url.split('/')
            public_id = '/'.join(parts[-3:]).rsplit('.', 1)[0]
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass  # optional: log this

        img.delete()
        return jsonify({"message": "Teeth image deleted successfully"}), 200


    @staticmethod
    def get_image_by_id(image_id):
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        img = UserImage.objects(id=image_id, user=user).first()
        if not img:
            return jsonify({"error": "Not found"}), 404

        return jsonify({
            "id":          str(img.id),
            "uploaded_at": img.uploaded_at.isoformat(),
            "image_url":   img.image_url
        }), 200
