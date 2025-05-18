from flask import request, jsonify
from models.doctor import Doctor
from models.user import User
from models.time_slot import TimeSlot
from flask_jwt_extended import get_jwt_identity
from models import db

class DoctorController:

    @staticmethod
    def list_doctors():
        doctors = Doctor.query.all()
        result = []
        for doctor in doctors:
            user = User.query.get(doctor.user_id)

            # Sort time slots by date and time, then get the first one
            sorted_slots = sorted(
                doctor.time_slots,
                key=lambda s: (s.available_date, s.start_time)
            )
            closest_slot = sorted_slots[0] if sorted_slots else None

            availability = None
            if closest_slot:
                availability = {
                    "day": closest_slot.available_day.value,
                    "date": str(closest_slot.available_date),
                    "start_time": closest_slot.start_time.strftime("%H:%M"),
                    "end_time": closest_slot.end_time.strftime("%H:%M")
                }

            result.append({
                "id": doctor.doctor_id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "national_id": user.national_id,
                "address": user.address,
                "profile_picture_url": user.profile_picture_url,
                "gender": user.gender.value,
                "specialization": doctor.specialization,
                "consultation_fee": doctor.consultation_fee,
                "title": doctor.title.value,
                "experience_years": doctor.experience_years,
                "average_rating": doctor.average_rating,
                "bio": doctor.bio,
                "availability": availability  # renamed key for clarity
            })
        return jsonify(result), 200


    @staticmethod
    def get_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        user = User.query.get(doctor.user_id)

        slots = TimeSlot.query.filter_by(doctor_id=doctor_id).all()
        availability = [
            {
                "day": slot.day_of_week,
                "date": slot.available_date,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M")
            }
            for slot in slots
        ]

        return jsonify({
            "id": doctor.doctor_id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "national_id": user.national_id,
            "address": user.address,
            "profile_picture_url": user.profile_picture_url,
            "gender": user.gender.value,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "specialization": doctor.specialization,
            "consultation_fee": doctor.consultation_fee,
            "title": doctor.title.value,
            "experience_years": doctor.experience_years,
            "average_rating": doctor.average_rating,
            "bio": doctor.bio,
            "availability": availability
        }), 200

    @staticmethod
    def get_availability(doctor_id):
        slots = TimeSlot.query.filter_by(doctor_id=doctor_id).all()
        if not slots:
            return jsonify({"message": "No availability found"}), 404

        availability = [{
            "id": slot.slot_id,
            "day": slot.day_of_week,
            "date": slot.available_date,
            "start_time": str(slot.start_time),
            "end_time": str(slot.end_time)
        } for slot in slots]

        return jsonify({"availability": availability}), 200

    @staticmethod
    def update_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        data = request.json
        doctor.specialization = data.get("specialization", doctor.specialization)
        doctor.bio = data.get("bio", doctor.bio)
        doctor.experience_years = data.get("experience_years", doctor.experience_years)
        db.session.commit()

        return jsonify({"message": "Doctor profile updated successfully"}), 200
