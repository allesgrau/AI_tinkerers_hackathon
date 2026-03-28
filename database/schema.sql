PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    pesel TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    enrolled_voice_sample TEXT,
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

CREATE TABLE IF NOT EXISTS auth_sessions (
    auth_session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT NOT NULL UNIQUE,
    patient_pesel TEXT,
    sms_code TEXT,
    sms_sent_at TEXT,
    sms_verified INTEGER NOT NULL DEFAULT 0 CHECK (sms_verified IN (0, 1)),
    voice_verification_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (voice_verification_status IN ('pending', 'passed', 'failed', 'skipped')),
    voice_similarity_score REAL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS voiceprints (
    voiceprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_pesel TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    model_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_call_id ON auth_sessions (call_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_patient ON auth_sessions (patient_pesel);
CREATE INDEX IF NOT EXISTS idx_voiceprints_patient ON voiceprints (patient_pesel);
