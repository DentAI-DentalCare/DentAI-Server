from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from models import db
from models.appointment import Appointment
from models.doctor import Doctor
from models.time_slot import TimeSlot
from models.user import User
from datetime import datetime


class AppointmentController:

    @staticmethod
    def book_appointment():
        data = request.json
        doctor_id = data.get("doctor_id")
        date = data.get("appointment_date")
        slot_id = data.get("time_slot_id")
        notes = data.get("notes", "")
        print(f"Data received for booking: {data}")  # Debugging line

        if not all([doctor_id, date, slot_id]):
            return jsonify({"error": "Missing required fields"}), 400

        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Fetch selected time slot
        slot = TimeSlot.query.filter_by(slot_id=slot_id, doctor_id=doctor_id, available_date=date).first()
        if not slot:
            return jsonify({"error": "Time slot not found or invalid"}), 404


        appointment = Appointment(
            patient_id=user.user_id,
            doctor_id=doctor_id,
            appointment_date=date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status="Scheduled",
            notes=notes
        )
        db.session.add(appointment)
        db.session.commit()

        return jsonify({"message": "Appointment booked successfully"}), 201

  
    @staticmethod
    def get_my_appointments():
        user_email = get_jwt_identity()
        claims = get_jwt()
        role = claims.get("role")

        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if role == "Patient":
            appointments = Appointment.query.filter_by(patient_id=user.user_id).all()
        elif role == "Doctor":
            doctor = Doctor.query.filter_by(user_id=user.user_id).first()
            appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).all()
        else:
            return jsonify({"error": "Unauthorized role"}), 403

        result = [{
            "id": a.appointment_id,
            "date": a.appointment_date.isoformat(),
            "start_time": str(a.start_time),
            "end_time": str(a.end_time),
            "status": a.status.value,
            "notes": a.notes,
            "doctor_name": f"{a.doctor.user.first_name} {a.doctor.user.last_name}" if a.doctor and a.doctor.user else "N/A",
            "specialization": a.doctor.specialization if a.doctor else "N/A",
            "consultation_fee": a.doctor.consultation_fee if a.doctor else "N/A",
            "doctor_profile_picture": a.doctor.user.profile_picture_url if a.doctor else "N/A"
        } for a in appointments]


        return jsonify(result), 200

    @staticmethod
    def cancel_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        # Delete the appointment record
        db.session.delete(appointment)
        db.session.commit()

        return jsonify({"message": "Appointment cancelled and deleted successfully"}), 200


    @staticmethod
    def complete_appointment(appointment_id):
        data = request.json
        diagnosis = data.get("diagnosis", "")
        treatment_plan = data.get("treatment_plan", "")

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        appointment.status = "Completed"
        appointment.diagnosis = diagnosis
        appointment.treatment_plan = treatment_plan
        db.session.commit()

        return jsonify({"message": "Appointment marked as completed"}), 200

    @staticmethod
    def get_available_timeslots(doctor_id):
        # Get all time slots for the doctor across all dates
        slots = TimeSlot.query.filter_by(doctor_id=doctor_id).all()

        timeslot_list = []
        for slot in slots:
            timeslot_list.append({
                "id": slot.slot_id,
                "date": str(slot.available_date),
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time)
            })

        return jsonify(timeslot_list), 200
