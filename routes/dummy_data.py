# controllers/dummy_controller.py

from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from faker import Faker
from datetime import datetime, timedelta, time
from model import (
    db,
    User,
    Doctor,
    TimeSlot,
    Appointment, 
    UserImage,
    RoleEnum,
    TitleEnum,
    DayEnum
)
import random
import cloudinary
import os

dummy_blueprint = Blueprint("dummy", __name__)
fake = Faker("ar_EG")  # Egyptian locale

@dummy_blueprint.route("/create-dummy-data", methods=["POST"])
def create_dummy_data():
    try:
        # ─── Clear Cloudinary doctor folders ──────────────────────────────
        for user in User.objects(role=RoleEnum.Doctor):
            folder = user.email.split("@")[0]
            try:
                cloudinary.api.delete_resources_by_prefix(folder)
                cloudinary.api.delete_folder(folder)
            except Exception:
                pass  # ignore any Cloudinary errors

        # ─── Drop all collections ─────────────────────────────────────────
        Appointment.drop_collection()
        TimeSlot.drop_collection()
        Doctor.drop_collection()
        UserImage.drop_collection()
        User.drop_collection()

        phone_prefixes = ["010", "011", "012", "015"]

        # ─── Create 5 Arabic-named patients ───────────────────────────────
        arabic_patient_names = [
            ("Salma", "Nasser"),
            ("Khaled", "Adel"),
            ("Aya", "Mostafa"),
            ("Youssef", "Hani"),
            ("Farah", "Tarek")
        ]
        # Short clinic addresses to use
        clinic_addresses = [
    "ToothCare Clinic, 15 Talaat Harb St., Downtown, Cairo",
    "Bright Dental, 8 El Merghany St., Heliopolis, Cairo",
    "Smile Hub, 12 El Horreya St., Zamalek, Cairo",
    "Pearl Dental, 5 Abbas El Akkad St., Nasr City, Cairo",
    "Elite Dental, 3 Al Mesaha St., Dokki, Giza",
    "Care Dental, 9 El Laselky St., Maadi, Cairo",
    "Shiny Teeth, 2 Al Orouba St., Heliopolis, Cairo",
    "White Smile, 6 El Thawra St., Mohandessin, Giza"
]

        patients = []
        for first_name, last_name in arabic_patient_names:
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            phone = random.choice(phone_prefixes) + "".join(str(random.randint(0,9)) for _ in range(9))
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                national_id=int("2" + "".join(str(random.randint(0,9)) for _ in range(13))),
                phone_number=phone,
                address=fake.address().replace("\n", " "),
                password=generate_password_hash("pass"),
                role=RoleEnum.Patient,
                profile_picture_url="",
                gender=fake.random_element(["male", "female"]),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=60),
                created_at=datetime.utcnow()
            )
            user.save()
            patients.append(user)

        # ─── Create 8 doctors with Cloudinary images ─────────────────────
        male_doctor_names   = ["Mohamed Hesham", "Ahmed Sameh", "Omar Nader", "Tarek Mohamed"]
        female_doctor_names = ["Menna Khaled","Malak Ramy", "Laila Amr", "Mona Hassan"]
        doctor_names        = male_doctor_names + female_doctor_names
        doctor_genders      = ["male"]*4 + ["female"]*4

        male_photos_dir   = "C:/Users/samir/Downloads/doctors/male"
        female_photos_dir = "C:/Users/samir/Downloads/doctors/female"
        male_photos   = sorted(os.path.join(male_photos_dir, f) for f in os.listdir(male_photos_dir))
        female_photos = sorted(os.path.join(female_photos_dir, f) for f in os.listdir(female_photos_dir))
        doctor_photos  = male_photos + female_photos

        doctors = []
        for i in range(8):
            first_name, last_name = doctor_names[i].split()
            gender               = doctor_genders[i]
            photo_path           = doctor_photos[i]
            phone                = random.choice(phone_prefixes) + "".join(str(random.randint(0,9)) for _ in range(9))
            email                = f"{first_name.lower()}.{last_name.lower()}@gmail.com"

            # upload profile photo
            upload_res = cloudinary.uploader.upload(photo_path, folder=f"{email}/profile")
            photo_url  = upload_res.get("secure_url", "")

            # create user doc
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                national_id=int("2" + "".join(str(random.randint(0,9)) for _ in range(13))),
                phone_number=phone,
                address=fake.address().replace("\n", " "),
                password=generate_password_hash("pass"),
                role=RoleEnum.Doctor,
                profile_picture_url=photo_url,
                gender=gender,
                birth_date=fake.date_of_birth(minimum_age=28, maximum_age=65),
                created_at=datetime.utcnow()
            )
            user.save()

            # create doctor profile
            title_str = fake.random_element([t.value for t in TitleEnum])
            doctor = Doctor(
                user=user,
                specialization=fake.random_element([
                    "Orthodontics", "Periodontics", "Implantology", "Cosmetic Dentistry",
                    "Endodontics", "Prosthodontics", "Adult Dentistry", "Elder Dentistry",
                    "Pediatric Dentistry", "Oral and Maxillofacial Surgery", "Oral Radiology"
                ]),
                bio="Hi there! I’m a caring, patient-focused dentist dedicated to helping you smile with confidence. I specialize in preventive care and gentle cosmetic treatments, and I love teaching you the best techniques to keep your teeth healthy. I stay current with the latest dental technology so every visit is as comfortable and effective as possible. Let’s work together to make your smile shine!",
                experience_years=random.randint(1, 30),
                clinic_address=clinic_addresses[i % len(clinic_addresses)],  # Sequential assignment
                consultation_fee=random.choice(list(range(200, 2001, 50))),
                average_rating=random.choice([2.5, 3.0, 3.5, 4.0, 4.5, 5.0]),
                title=TitleEnum(title_str)
            )
            doctor.save()
            doctors.append((user, doctor))

        # ─── Create Time Slots for next 11 days ───────────────────────────
        for _, doctor in doctors:
            for day_offset in range(11):
                date_obj = (datetime.utcnow() + timedelta(days=day_offset)).date()
                day_name = date_obj.strftime("%A")
                slot_start = random.choice([
                    time(h, m) for h in range(13, 17) for m in (0,30)
                ])
                slot_end   = random.choice([
                    time(22,0), time(23,0), time(0,0)
                ])

                ts = TimeSlot(
                    doctor=doctor,
                    available_day=DayEnum[day_name],
                    available_date=date_obj,
                    start_time=slot_start.strftime("%H:%M:%S"),
                    end_time=slot_end.strftime("%H:%M:%S")
                )
                ts.save()

        return jsonify({"message": "All dummy data created successfully ✅"}), 201

    except Exception as e:
        # no DB rollback needed for MongoEngine
        return jsonify({"error": str(e)}), 500
