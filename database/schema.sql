PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    pesel TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    verification_zip TEXT NOT NULL,
    CHECK (length(pesel) = 11),
    CHECK (pesel GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]')
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE,
    specialty TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_pesel TEXT,
    appointment_datetime TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Available', 'Booked')),
    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE SET NULL,
    CHECK (
        (status = 'Available' AND patient_pesel IS NULL) OR
        (status = 'Booked' AND patient_pesel IS NOT NULL)
    ),
    UNIQUE (doctor_id, appointment_datetime)
);

CREATE INDEX IF NOT EXISTS idx_doctors_specialty ON doctors (specialty);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_datetime ON appointments (doctor_id, appointment_datetime);
CREATE INDEX IF NOT EXISTS idx_appointments_status_datetime ON appointments (status, appointment_datetime);
