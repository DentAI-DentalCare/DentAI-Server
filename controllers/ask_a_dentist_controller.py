# controllers/ask_a_dentist_controller.py

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
import cloudinary.uploader

from model import (
    User,
    Doctor,
    UserImage,
    ConsultationThread,
    ConsultationMessage,
    RoleEnum
)

class AskADentistController:

    @staticmethod
    def get_all_doctors_info():
        doctors = Doctor.objects()
        result = []
        for doc in doctors:
            usr = doc.user
            if not usr: continue
            result.append({
                "doctor_id":           str(doc.id),
                "id":                  str(usr.id),
                "profile_picture_url": usr.profile_picture_url,
                "name":                f"{usr.first_name} {usr.last_name}",
                "specialization":      doc.specialization
            })
        return jsonify({"doctors": result}), 200

    @staticmethod
    def send_message():
        current_email     = get_jwt_identity()
        user              = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        raw_ids     = request.form.get("recipient_id", "")
        message_txt = request.form.get("message", "")
        img_file    = request.files.get("file")

        if not raw_ids or (not message_txt and not img_file):
            return jsonify({
                "error": "recipient_id and message or image file are required"
            }), 400

        recipient_ids = [rid.strip() for rid in raw_ids.split(",")]

        # upload once
        image_url = None
        img_rec   = None
        if img_file:
            up = cloudinary.uploader.upload(
                img_file, folder=f"{user.email}/consultations"
            )
            image_url = up.get("secure_url")
            img_rec   = UserImage(user=user, image_url=image_url, diagnosis={})
            img_rec.save()

        sent_to = []
        for rid in recipient_ids:
            if user.role is RoleEnum.Doctor:
                doctor  = Doctor.objects(user=user).first()
                patient = User.objects(id=rid).first()
            else:
                patient = user
                # rid is Doctor.id
                doctor  = Doctor.objects(id=rid).first()

            if not doctor or not patient:
                continue

            # find/create thread
            thread = ConsultationThread.objects(
                doctor=doctor, patient=patient
            ).first()
            if not thread:
                thread = ConsultationThread(
                    doctor=doctor,
                    patient=patient,
                    image=img_rec
                )
                thread.save()

            # save message
            sender_role = RoleEnum.Doctor if user.role is RoleEnum.Doctor else RoleEnum.Patient
            msg = ConsultationMessage(
                thread=thread,
                sender_role=sender_role,
                message=message_txt,
                image_url=image_url
            )
            msg.save()
            sent_to.append(rid)

        return jsonify({
            "message":          "Message sent successfully",
            "sent_to_user_ids": sent_to
        }), 201

    @staticmethod
    def get_my_conversations():
        current_email = get_jwt_identity()
        user          = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        result = []
        if user.role is RoleEnum.Doctor:
            doctor  = Doctor.objects(user=user).first()
            threads = ConsultationThread.objects(doctor=doctor)
            for t in threads:
                p    = t.patient
                last = ConsultationMessage.objects(thread=t).order_by('-sent_at').first()
                text = "[Image]" if last and not last.message and last.image_url else (last.message or "")
                result.append({
                    "user_id":             str(p.id),
                    "user_name":           f"{p.first_name} {p.last_name}",
                    "profile_picture_url": p.profile_picture_url,
                    "last_message":        text,
                    "last_message_date":   last.sent_at.isoformat() if last else None
                })
        else:
            docs    = Doctor.objects()
            threads = {t.doctor.id: t for t in ConsultationThread.objects(patient=user)}
            for doc in docs:
                usr    = doc.user
                thread = threads.get(doc.id)
                if thread:
                    last = ConsultationMessage.objects(thread=thread).order_by('-sent_at').first()
                    text = "[Image]" if last and not last.message and last.image_url else (last.message or "")
                    date = last.sent_at.isoformat() if last else None
                else:
                    text, date = "", None

                result.append({
                    "user_id":           str(doc.id),               # <-- changed here
                    "specialization":      doc.specialization,
                    "user_name":           f"{usr.first_name} {usr.last_name}",
                    "profile_picture_url": usr.profile_picture_url,
                    "last_message":        text,
                    "last_message_date":   date
                })

        result.sort(key=lambda x: x['last_message_date'] or "", reverse=True)
        return jsonify({"conversations": result}), 200


    @staticmethod
    def get_thread_with_user(user_id):
        current_email = get_jwt_identity()
        user          = User.objects(email=current_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role is RoleEnum.Doctor:
            doctor  = Doctor.objects(user=user).first()
            patient = User.objects(id=user_id).first()
        else:
            patient = user
            doctor  = Doctor.objects(id=user_id).first()

        if not doctor or not patient:
            return jsonify({"error": "Doctor or patient not found"}), 404

        thread = ConsultationThread.objects(
            doctor=doctor, patient=patient
        ).first()
        if not thread:
            thread = ConsultationThread(doctor=doctor, patient=patient)
            thread.save()

        messages = ConsultationMessage.objects(thread=thread).order_by('sent_at')
        return jsonify({
            "messages": [
                {
                    "sender":    m.sender_role.name,
                    "message":   m.message,
                    "image_url": m.image_url,
                    "sent_at":   m.sent_at.isoformat()
                } for m in messages
            ]
        }), 200
