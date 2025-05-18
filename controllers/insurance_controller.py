from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db
from models.user import User
from models.user_insurance import UserInsurance
import cloudinary.uploader
from urllib.parse import unquote

class InsuranceController:

    @staticmethod
    def add_insurance():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.form
        company_name = data.get("company_name")
        insurance_number = data.get("insurance_number")
        expiry_date = data.get("expiry_date")

        if "card_image" not in request.files:
            return jsonify({"error": "Image file required"}), 400

        file = request.files["card_image"]
        upload_result = cloudinary.uploader.upload(
            file, folder=f"{user.email}/insurance"
        )
        image_url = upload_result["secure_url"]

        insurance = UserInsurance(
            user_id=user.user_id,
            company_name=company_name,
            insurance_number=insurance_number,
            expiry_date=expiry_date,
            card_image_url=image_url
        )

        db.session.add(insurance)
        db.session.commit()

        return jsonify({"message": "Insurance added", "image_url": image_url}), 201

    @staticmethod
    def update_insurance(insurance_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        insurance = UserInsurance.query.filter_by(insurance_id=insurance_id, user_id=user.user_id).first()

        if not insurance:
            return jsonify({"error": "Insurance not found"}), 404

        data = request.form
        insurance.insurance_number = data.get("insurance_number", insurance.insurance_number)
        insurance.expiry_date = data.get("expiry_date", insurance.expiry_date)

        if "card_image" in request.files:
            if insurance.card_image_url:
                public_id_encoded = '/'.join(insurance.card_image_url.split('/')[7:]).rsplit('.', 1)[0]
                public_id = unquote(public_id_encoded)
                cloudinary.uploader.destroy(public_id)

            file = request.files["card_image"]
            upload_result = cloudinary.uploader.upload(file, folder=f"{user.email}/insurance")
            insurance.card_image_url = upload_result["secure_url"]

        db.session.commit()
        return jsonify({"message": "Insurance updated"}), 200

    @staticmethod
    def delete_insurance(insurance_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()
        insurance = UserInsurance.query.filter_by(insurance_id=insurance_id, user_id=user.user_id).first()

        if not insurance:
            return jsonify({"error": "Insurance not found"}), 404

        if insurance.card_image_url:
            public_id_encoded = '/'.join(insurance.card_image_url.split('/')[7:]).rsplit('.', 1)[0]
            public_id = unquote(public_id_encoded)
            cloudinary.uploader.destroy(public_id)

        db.session.delete(insurance)
        db.session.commit()

        return jsonify({"message": "Insurance deleted"}), 200

    @staticmethod
    def get_all_insurances():
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        insurances = UserInsurance.query.filter_by(user_id=user.user_id).all()

        result = []
        for ins in insurances:
            result.append({
                "id": ins.insurance_id,
                "company_name": ins.company_name,
                "insurance_number": ins.insurance_number,
                "expiry_date": ins.expiry_date,
                "card_image_url": ins.card_image_url
            })

        return jsonify(result), 200
