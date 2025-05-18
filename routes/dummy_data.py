from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from faker import Faker
from datetime import datetime, timedelta, time
from models import db
from models.doctor import Doctor
from models.user import User
from models.time_slot import TimeSlot
from models.appointment import Appointment
from models.user_image import UserImage
import random, cloudinary
import os

dummy_blueprint = Blueprint("dummy", __name__)
fake = Faker("ar_EG")  # Egyptian locale

@dummy_blueprint.route("/create-dummy-data", methods=["POST"])
def create_dummy_data():
    try:
           # Clear all Cloudinary doctor folders
        existing_users = User.query.filter_by(role="Doctor").all()
        for user in existing_users:
            folder = f"{user.email.split('@')[0]}"
            try:
                cloudinary.api.delete_resources_by_prefix(folder)
                cloudinary.api.delete_folder(folder)
            except Exception:
                continue
        # Clear existing data
        db.session.query(Appointment).delete()
        db.session.query(TimeSlot).delete()
        db.session.query(Doctor).delete()
        db.session.query(UserImage).delete()
        db.session.query(User).delete()
        db.session.commit()

        phone_prefixes = ["010", "011", "012", "015"]
       # Doctor data
        male_doctor_names = ["Mohamed Hesham", "Ahmed Sameh", "Omar Nader", "Tarek Mohamed"]
        female_doctor_names = ["Laila Amr", "Mona Hassan", "Malak Ramy", "Nour Khaled"]
        doctor_names = male_doctor_names + female_doctor_names
        doctor_genders = ["male"] * 4 + ["female"] * 4

        # Doctor photo paths
        male_photos_dir = "C:/Users/samir/Downloads/doctors/male"
        female_photos_dir = "C:/Users/samir/Downloads/doctors/female"
        male_photos = sorted([os.path.join(male_photos_dir, img) for img in os.listdir(male_photos_dir)])
        female_photos = sorted([os.path.join(female_photos_dir, img) for img in os.listdir(female_photos_dir)])
        doctor_photos = male_photos + female_photos

        # # Create 5 fake patients
        # for i in range(5):
        #     gender = fake.random_element(["male", "female"])
        #     full_name = fake.name_male() if gender == "male" else fake.name_female()
        #     first_name, last_name = full_name.split(" ", 1) if " " in full_name else (full_name, "")
        #     email = f"{first_name.lower()}{i}@gmail.com"
        #     patient = User(
        #         first_name=first_name,
        #         last_name=last_name,
        #         email=email,
        #         national_id=int('2' + ''.join([str(random.randint(0, 9)) for _ in range(13)])),
        #         phone_number="01" + ''.join([str(random.randint(0, 9)) for _ in range(9)]),
        #         address=fake.address().replace("\n", " "),
        #         password=generate_password_hash("pass"),
        #         role="Patient",
        #         profile_picture_url="",
        #         gender=gender,
        #         birth_date=fake.date_of_birth(minimum_age=18, maximum_age=60),
        #     )
        #     db.session.add(patient)

        patients = []

        # Create 5 Arabic-named patients
        arabic_patient_names = [
            ("Salma", "Nasser"),
            ("Khaled", "Adel"),
            ("Aya", "Mostafa"),
            ("Youssef", "Hani"),
            ("Farah", "Tarek")
        ]

        for i, (first_name, last_name) in enumerate(arabic_patient_names):
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            phone_start = random.choice(phone_prefixes)
            patient = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                national_id=int('2' + ''.join([str(random.randint(0, 9)) for _ in range(13)])),
                phone_number=phone_start + ''.join([str(random.randint(0, 9)) for _ in range(9)]),
                address=fake.address().replace("\n", " "),
                password=generate_password_hash("pass"),
                role="Patient",
                profile_picture_url="",
                gender=fake.random_element(["male", "female"]),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=60),
            )
            db.session.add(patient)
            patients.append(patient)

        db.session.commit()
        doctors = []

        # Create 8 doctors with Arabic-style names and Cloudinary images
        for i in range(8):
            first_name, last_name = doctor_names[i].split()
            gender = doctor_genders[i]
            photo_path = doctor_photos[i]
            phone_start = random.choice(phone_prefixes)

            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"

            # Upload to Cloudinary in folder based on email
            folder_path = f"{email}/profile"
            upload_result = cloudinary.uploader.upload(photo_path, folder=folder_path)
            photo_url = upload_result["secure_url"]

            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                national_id=int('2' + ''.join([str(random.randint(0, 9)) for _ in range(13)])),
                phone_number=phone_start + ''.join([str(random.randint(0, 9)) for _ in range(9)]),
                address=fake.address().replace("\n", " "),
                password=generate_password_hash("pass"),
                role="Doctor",
                profile_picture_url=photo_url,
                gender=gender,
                birth_date=fake.date_of_birth(minimum_age=28, maximum_age=65),
            )
            db.session.add(user)
            db.session.flush()

            doctor = Doctor(
                user_id=user.user_id,
                specialization=fake.random_element([
                    "Orthodontics", "Periodontics", "Implantology", "Cosmetic Dentistry",
                    "Endodontics", "Prosthodontics", "Adult Dentistry", "Elder Dentistry",
                    "Pediatric Dentistry", "Oral and Maxillofacial Surgery", "Oral Radiology"
                ]),
                bio=fake.text(max_nb_chars=250),
                experience_years=random.randint(1, 30),
                consultation_fee=random.choice(range(200, 2001, 50)),
                average_rating=random.choice([2.5, 3.0, 3.5, 4.0, 4.5, 5.0]),
                title=fake.random_element(["Lecturer", "Professor", "Consultant", "Specialist", "Dentist"])
            )
            db.session.add(doctor)
            db.session.flush()
            doctors.append((user, doctor))


        # --- Create Time Slots ---
        for _, doctor in doctors:
            for day_offset in range(11):
                date_obj = (datetime.today() + timedelta(days=day_offset)).date()
                day_name = date_obj.strftime("%A")

                possible_times = [
                    time(hour, minute)
                    for hour in range(13, 17)
                    for minute in (0, 30)
                ]
                start_time = random.choice(possible_times)
                end_time = random.choice([
                    time(22, 0),
                    time(23, 0),
                    time(0, 0)
                ])

                timeslot = TimeSlot(
                    doctor_id=doctor.doctor_id,
                    available_day=day_name,
                    available_date=date_obj,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(timeslot)

        db.session.commit()

        # # --- Create Appointments ---
        # all_slots = TimeSlot.query.all()
        # for i in range(10):
        #     slot = random.choice(all_slots)
        #     appointment = Appointment(
        #         patient_id=patients[i % len(patients)].user_id,
        #         doctor_id=slot.doctor_id,
        #         appointment_date=slot.available_date,
        #         start_time=slot.start_time,
        #         end_time=slot.end_time,
        #         status=fake.random_element(["Scheduled", "Completed", "Cancelled"]),
        #         notes=fake.sentence(),
        #         diagnosis=fake.sentence(),
        #         treatment_plan=fake.sentence()
        #     )
        #     db.session.add(appointment)

        # db.session.commit()


        return jsonify({"message": "All dummy data created successfully ✅"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
