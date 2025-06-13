# controllers/doctor_controller.py

from flask import request, jsonify
from model import User, Doctor, TimeSlot
from flask_jwt_extended import get_jwt_identity  # if you need auth, otherwise omit


class DoctorController:

    @staticmethod
    def list_doctors():
        doctors = Doctor.objects()
        result = []
        for doc in doctors:
            user = doc.user  # ReferenceField to User

            # fetch and sort this doctor's time slots
            slots = TimeSlot.objects(doctor=doc)
            sorted_slots = sorted(
                slots,
                key=lambda s: (s.available_date, s.start_time)
            )
            closest = sorted_slots[0] if sorted_slots else None

            availability = None
            if closest:
                availability = {
                    "day":        closest.available_day.name,
                    "date":       closest.available_date.isoformat(),
                    "start_time": closest.start_time,  # already "HH:MM:SS"
                    "end_time":   closest.end_time,
                }

            result.append({
                "id":                   str(doc.id),
                "name":                 f"{user.first_name} {user.last_name}",
                "email":                user.email,
                "national_id":          user.national_id,
                "address":              user.address,
                "profile_picture_url":  user.profile_picture_url,
                "gender":               user.gender.name,
                "specialization":       doc.specialization,
                "consultation_fee":     doc.consultation_fee,
                "title":                doc.title.name,
                "experience_years":     doc.experience_years,
                "average_rating":       doc.average_rating,
                "bio":                  doc.bio,
                "availability":         availability,
            })
        return jsonify(result), 200


    @staticmethod
    def get_doctor(doctor_id):
        doc = Doctor.objects(id=doctor_id).first()
        if not doc:
            return jsonify({"error": "Doctor not found"}), 404

        user = doc.user

        slots = TimeSlot.objects(doctor=doc)
        availability = [
            {
                "day":        slot.available_day.name,
                "date":       slot.available_date.isoformat(),
                "start_time": slot.start_time,
                "end_time":   slot.end_time
            }
            for slot in slots
        ]

        return jsonify({
            "id":                   str(doc.id),
            "name":                 f"{user.first_name} {user.last_name}",
            "email":                user.email,
            "national_id":          user.national_id,
            "address":              user.address,
            "profile_picture_url":  user.profile_picture_url,
            "gender":               user.gender.name,
            "birth_date":           user.birth_date.isoformat() if user.birth_date else None,
            "specialization":       doc.specialization,
            "consultation_fee":     doc.consultation_fee,
            "title":                doc.title.name,
            "experience_years":     doc.experience_years,
            "average_rating":       doc.average_rating,
            "bio":                  doc.bio,
            "availability":         availability
        }), 200


    @staticmethod
    def get_availability(doctor_id):
        doc = Doctor.objects(id=doctor_id).first()
        if not doc:
            return jsonify({"message": "No availability found"}), 404

        slots = TimeSlot.objects(doctor=doc)
        if not slots:
            return jsonify({"message": "No availability found"}), 404

        availability = [{
            "id":          str(slot.id),
            "day":         slot.available_day.name,
            "date":        slot.available_date.isoformat(),
            "start_time":  slot.start_time,
            "end_time":    slot.end_time
        } for slot in slots]

        return jsonify({"availability": availability}), 200


    @staticmethod
    def update_doctor(doctor_id):
        doc = Doctor.objects(id=doctor_id).first()
        if not doc:
            return jsonify({"error": "Doctor not found"}), 404

        data = request.get_json() or {}
        doc.specialization   = data.get("specialization", doc.specialization)
        doc.bio              = data.get("bio", doc.bio)
        doc.experience_years = data.get("experience_years", doc.experience_years)
        doc.save()

        return jsonify({"message": "Doctor profile updated successfully"}), 200
