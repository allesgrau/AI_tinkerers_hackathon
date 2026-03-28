PATIENTS = [
    {
        "pesel": "02211312345",
        "full_name": "John Smith",
        "phone_number": "+12025550101",
        "verification_zip": "10001",
    },
    {
        "pesel": "83051298765",
        "full_name": "Mary Johnson",
        "phone_number": "+12025550102",
        "verification_zip": "10002",
    },
    {
        "pesel": "99123145678",
        "full_name": "Peter Miller",
        "phone_number": "+12025550103",
        "verification_zip": "10003",
    },
]

DOCTORS = [
    {"full_name": "Dr. Emily Carter", "specialty": "Cardiologist"},
    {"full_name": "Dr. Michael Brown", "specialty": "Pediatrician"},
    {"full_name": "Dr. Sarah Wilson", "specialty": "GP"},
]

APPOINTMENT_SLOTS = [
    {"doctor_full_name": "Dr. Emily Carter", "appointment_datetime": "2026-03-29 09:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Emily Carter", "appointment_datetime": "2026-03-29 09:30", "patient_pesel": "02211312345", "status": "Booked"},
    {"doctor_full_name": "Dr. Emily Carter", "appointment_datetime": "2026-03-29 10:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Michael Brown", "appointment_datetime": "2026-03-29 11:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Michael Brown", "appointment_datetime": "2026-03-29 11:30", "patient_pesel": "83051298765", "status": "Booked"},
    {"doctor_full_name": "Dr. Sarah Wilson", "appointment_datetime": "2026-03-29 14:00", "patient_pesel": None, "status": "Available"},
    {"doctor_full_name": "Dr. Sarah Wilson", "appointment_datetime": "2026-03-29 14:30", "patient_pesel": "99123145678", "status": "Booked"},
]
