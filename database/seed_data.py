PATIENTS = [
    {
        "pesel": "02211312345",
        "full_name": "Jan Kowalski",
        "phone_number": "+48501111222",
        "verification_zip": "00-001",
    },
    {
        "pesel": "83051298765",
        "full_name": "Maria Nowak",
        "phone_number": "+48503334455",
        "verification_zip": "30-002",
    },
    {
        "pesel": "99123145678",
        "full_name": "Piotr Zielinski",
        "phone_number": "+48507778899",
        "verification_zip": "80-003",
    },
]

DOCTORS = [
    {"full_name": "Dr. Anna Nowak", "specialty": "Cardiologist"},
    {"full_name": "Dr. Tomasz Wisniewski", "specialty": "Pediatrician"},
    {"full_name": "Dr. Katarzyna Lewandowska", "specialty": "GP"},
]

APPOINTMENT_SLOTS = [
    {"doctor_full_name": "Dr. Anna Nowak", "appointment_datetime": "2026-03-29 09:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Anna Nowak", "appointment_datetime": "2026-03-29 09:30", "patient_pesel": "02211312345", "status": "Booked"},
    {"doctor_full_name": "Dr. Anna Nowak", "appointment_datetime": "2026-03-29 10:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Tomasz Wisniewski", "appointment_datetime": "2026-03-29 11:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Tomasz Wisniewski", "appointment_datetime": "2026-03-29 11:30", "patient_pesel": "83051298765", "status": "Booked"},
    {"doctor_full_name": "Dr. Katarzyna Lewandowska", "appointment_datetime": "2026-03-29 14:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Katarzyna Lewandowska", "appointment_datetime": "2026-03-29 14:30", "patient_pesel": "99123145678", "status": "Booked"},
]
