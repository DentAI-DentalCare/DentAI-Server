# controllers/insurance_controller.py

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from urllib.parse import unquote
import cloudinary.uploader
import json

from model import User, UserInsurance


class InsuranceController:

    @staticmethod
    def add_insurance():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        form = request.form
        company_name     = form.get("company_name")
        insurance_number = form.get("insurance_number")
        expiry_date      = form.get("expiry_date")

        if not company_name or not insurance_number or not expiry_date:
            return jsonify({"error": "company_name, insurance_number and expiry_date are required"}), 400

        if "card_image" not in request.files:
            return jsonify({"error": "Image file required"}), 400

        file = request.files["card_image"]
        upload_res = cloudinary.uploader.upload(
            file,
            folder=f"{user.email}/insurance"
        )
        image_url = upload_res.get("secure_url")
        if not image_url:
            return jsonify({"error": "Cloudinary upload failed"}), 500

        insurance = UserInsurance(
            user=user,
            company_name=company_name,
            insurance_number=insurance_number,
            expiry_date=expiry_date,
            card_image_url=image_url
        )
        insurance.save()

        return jsonify({
            "message":    "Insurance added",
            "image_url":  image_url
        }), 201

    @staticmethod
    def update_insurance(insurance_id):
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        ins = UserInsurance.objects(id=insurance_id, user=user).first()
        if not ins:
            return jsonify({"error": "Insurance not found"}), 404

        form = request.form
        ins.insurance_number = form.get("insurance_number", ins.insurance_number)
        ins.expiry_date      = form.get("expiry_date", ins.expiry_date)

        if "card_image" in request.files:
            # remove old image
            if ins.card_image_url:
                # extract public_id
                parts    = ins.card_image_url.split('/')
                public_id = '/'.join(parts[-3:]).rsplit('.', 1)[0]
                public_id = unquote(public_id)
                try:
                    cloudinary.uploader.destroy(public_id)
                except Exception:
                    pass

            # upload new
            file      = request.files["card_image"]
            upload_res = cloudinary.uploader.upload(
                file,
                folder=f"{user.email}/insurance"
            )
            ins.card_image_url = upload_res.get("secure_url", ins.card_image_url)

        ins.save()
        return jsonify({"message": "Insurance updated"}), 200

    @staticmethod
    def delete_insurance(insurance_id):
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        ins = UserInsurance.objects(id=insurance_id, user=user).first()
        if not ins:
            return jsonify({"error": "Insurance not found"}), 404

        if ins.card_image_url:
            parts    = ins.card_image_url.split('/')
            public_id = '/'.join(parts[-3:]).rsplit('.', 1)[0]
            public_id = unquote(public_id)
            try:
                cloudinary.uploader.destroy(public_id)
            except Exception:
                pass

        ins.delete()
        return jsonify({"message": "Insurance deleted"}), 200

    @staticmethod
    def get_all_insurances():
        current_email = get_jwt_identity()
        user = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        ins_list = UserInsurance.objects(user=user)
        result = []
        for ins in ins_list:
            result.append({
                "id":               str(ins.id),
                "company_name":     ins.company_name,
                "insurance_number": ins.insurance_number,
                "expiry_date":      ins.expiry_date,
                "card_image_url":   ins.card_image_url
            })

        return jsonify(result), 200
