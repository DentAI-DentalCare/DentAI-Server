from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db
from models.consultation_message import ConsultationMessage, SenderRoleEnum
from models.consultation_thread import ConsultationThread
from models.user_image import UserImage
from models.user import User
from models.doctor import Doctor
import cloudinary.uploader


class ConsultationController:

    @staticmethod
    def get_all_doctors_info():
        doctors = Doctor.query.all()
        result = []

        for doctor in doctors:
            user = User.query.get(doctor.user_id)
            if user:
                result.append({
                    "doctor_id": doctor.doctor_id,
                    "user_id": user.user_id,
                    "profile_picture_url": user.profile_picture_url,
                    "name": f"{user.first_name} {user.last_name}",
                    "specialization": doctor.specialization
                })

        return jsonify({"doctors": result}), 200
   
    @staticmethod
    def send_message():
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        recipient_id = request.form.get("recipient_id")
        message_text = request.form.get("message")
        image_file = request.files.get("file")

        if not recipient_id or (not message_text and not image_file):
            return jsonify({"error": "Recipient and either message or image are required"}), 400

        # Determine doctor_id and patient_id
        if user.role.value == "Doctor":
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            if not doctor:
                return jsonify({"error": "Doctor not found"}), 404
            doctor_id = doctor.doctor_id
            patient_id = int(recipient_id)
        else:
            doctor = Doctor.query.filter_by(user_id=int(recipient_id)).first()
            if not doctor:
                return jsonify({"error": "Recipient is not a valid doctor"}), 404
            doctor_id = doctor.doctor_id
            patient_id = user.user_id

        # Check for existing thread
        thread = ConsultationThread.query.filter_by(
            patient_id=patient_id, doctor_id=doctor_id
        ).first()

        # Upload image if exists
        image_url = None
        image_record = None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file, folder=f"{user.email}/consultations")
            image_url = upload_result["secure_url"]
            image_record = UserImage(image_url=image_url, user_id=user.user_id)
            db.session.add(image_record)
            db.session.flush()

        # Create thread if not exists
        if not thread:
            thread = ConsultationThread(
                patient_id=patient_id,
                doctor_id=doctor_id,
                image_id=image_record.image_id if image_record else None
            )
            db.session.add(thread)
            db.session.flush()

        # Save message
        sender_role = SenderRoleEnum.Doctor if user.role.value == "Doctor" else SenderRoleEnum.Patient
        new_message = ConsultationMessage(
            thread_id=thread.thread_id,
            sender_role=sender_role,
            message=message_text,
            image_url=image_url
        )
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Message sent"}), 201


    @staticmethod
    def get_my_conversations():
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        result = []

        if user.role.value == "Doctor":
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            if not doctor:
                return jsonify({"error": "Doctor profile not found"}), 404

            threads = ConsultationThread.query.filter_by(doctor_id=doctor.doctor_id).all()
            for thread in threads:
                patient = User.query.get(thread.patient_id)
                last_msg = ConsultationMessage.query.filter_by(thread_id=thread.thread_id)\
                    .order_by(ConsultationMessage.sent_at.desc()).first()
                result.append({
                    "user_id": patient.user_id,
                    "user_name": f"{patient.first_name} {patient.last_name}",
                    "profile_picture_url": f"{patient.profile_picture_url}",
                    "last_message": last_msg.message if last_msg else "",
                    "last_message_date": last_msg.sent_at.isoformat() if last_msg else None
                })
        else:
            all_doctors = Doctor.query.all()
            threads = {
                thread.doctor_id: thread
                for thread in ConsultationThread.query.filter_by(patient_id=user.user_id).all()
            }

            for doctor in all_doctors:
                doctor_user = User.query.get(doctor.user_id)
                thread = threads.get(doctor.doctor_id)

                if thread:
                    last_msg = ConsultationMessage.query.filter_by(thread_id=thread.thread_id)\
                        .order_by(ConsultationMessage.sent_at.desc()).first()
                    result.append({
                        "user_id": doctor_user.user_id,
                        "specialization": doctor.specialization,
                        "user_name": f"{doctor_user.first_name} {doctor_user.last_name}",
                        "profile_picture_url": f"{doctor_user.profile_picture_url}",
                        "last_message": last_msg.message if last_msg else "",
                        "last_message_date": last_msg.sent_at.isoformat() if last_msg else None
                    })
                else:
                    result.append({
                        "user_id": doctor_user.user_id,
                        "specialization": doctor.specialization,
                        "user_name": f"{doctor_user.first_name} {doctor_user.last_name}",
                        "profile_picture_url": f"{doctor_user.profile_picture_url}",
                        "last_message": "",
                        "last_message_date": None
                    })

        result.sort(key=lambda x: x['last_message_date'] or "", reverse=True)
        return jsonify({"conversations": result}), 200

    @staticmethod
    def get_thread_with_user(user_id):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role.value == "Doctor":
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            thread = ConsultationThread.query.filter_by(doctor_id=doctor.doctor_id, patient_id=user_id).first()
        else:
            doctor = Doctor.query.filter_by(user_id=user_id).first()
            if not doctor:
                return jsonify({"error": "Doctor not found"}), 404
            thread = ConsultationThread.query.filter_by(patient_id=user.user_id, doctor_id=doctor.doctor_id).first()

        if not thread:
            # Create an empty thread (no image, no messages yet)
            thread = ConsultationThread(
                doctor_id=doctor.doctor_id if user.role.value != "Doctor" else doctor.doctor_id,
                patient_id=user.user_id if user.role.value != "Doctor" else user_id,
                image_id=None  # No image initially
            )
            db.session.add(thread)
            db.session.commit()


        messages = ConsultationMessage.query.filter_by(thread_id=thread.thread_id)\
            .order_by(ConsultationMessage.sent_at).all()

        return jsonify({
            "messages": [{
                "sender": msg.sender_role.value,
                "message": msg.message,
                "image_url": msg.image_url,
                "sent_at": msg.sent_at.isoformat()
            } for msg in messages]
        }), 200
