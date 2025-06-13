# controllers/appointment_controller.py

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime

from model import User, Doctor, TimeSlot, Appointment


class AppointmentController:

    @staticmethod
    def book_appointment():
        data      = request.get_json() or {}
        doctor_id = data.get("doctor_id")
        date      = data.get("appointment_date")
        slot_id   = data.get("time_slot_id")
        notes     = data.get("notes", "")

        if not all([doctor_id, date, slot_id]):
            return jsonify({"error": "Missing required fields"}), 400

        # find user
        user = User.objects(email=get_jwt_identity()).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # find doctor and slot
        doctor = Doctor.objects(id=doctor_id).first()
        slot   = TimeSlot.objects(id=slot_id, doctor=doctor, available_date=date).first()
        if not doctor or not slot:
            return jsonify({"error": "Time slot not found or invalid"}), 404

        # create appointment
        appt = Appointment(
            patient=user,
            doctor=doctor,
            appointment_date=date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            status="Scheduled",
            notes=notes
        )
        appt.save()

        return jsonify({"message": "Appointment booked successfully"}), 201


    @staticmethod
    def get_my_appointments():
        user_email = get_jwt_identity()
        claims     = get_jwt()
        role       = claims.get("role")

        user = User.objects(email=user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if role == "Patient":
            appts = Appointment.objects(patient=user)
        elif role == "Doctor":
            doctor = Doctor.objects(user=user).first()
            if not doctor:
                return jsonify({"error": "Doctor profile not found"}), 404
            appts = Appointment.objects(doctor=doctor)
        else:
            return jsonify({"error": "Unauthorized role"}), 403

        result = []
        for a in appts:
            doc = a.doctor
            usr = doc.user if doc else None

            result.append({
                "id":                    str(a.id),
                "date":                  a.appointment_date.isoformat(),
                "start_time":            a.start_time,
                "end_time":              a.end_time,
                "status":                a.status.name if hasattr(a.status, "name") else a.status,
                "notes":                 a.notes,
                "doctor_name":           f"{usr.first_name} {usr.last_name}" if usr else "N/A",
                "specialization":        doc.specialization if doc else "N/A",
                "consultation_fee":      doc.consultation_fee if doc else "N/A",
                "doctor_profile_picture": usr.profile_picture_url if usr else "N/A"
            })

        return jsonify(result), 200


    @staticmethod
    def cancel_appointment(appointment_id):
        appt = Appointment.objects(id=appointment_id).first()
        if not appt:
            return jsonify({"error": "Appointment not found"}), 404

        appt.delete()
        return jsonify({"message": "Appointment cancelled and deleted successfully"}), 200


    @staticmethod
    def complete_appointment(appointment_id):
        data           = request.get_json() or {}
        diagnosis      = data.get("diagnosis", "")
        treatment_plan = data.get("treatment_plan", "")

        appt = Appointment.objects(id=appointment_id).first()
        if not appt:
            return jsonify({"error": "Appointment not found"}), 404

        appt.status         = "Completed"
        appt.diagnosis      = diagnosis
        appt.treatment_plan = treatment_plan
        appt.save()

        return jsonify({"message": "Appointment marked as completed"}), 200


    @staticmethod
    def get_available_timeslots(doctor_id):
        doctor = Doctor.objects(id=doctor_id).first()
        if not doctor:
            return jsonify({"message": "No availability found"}), 404

        slots = TimeSlot.objects(doctor=doctor)
        timeslot_list = [{
            "id":         str(slot.id),
            "date":       slot.available_date.isoformat(),
            "start_time": slot.start_time,
            "end_time":   slot.end_time
        } for slot in slots]

        return jsonify(timeslot_list), 200
