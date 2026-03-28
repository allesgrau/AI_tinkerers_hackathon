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

-- ============ AUTH TABLES (Person 4 - Auth + Integracje) ============
-- Enhanced with Person 1 (Voice) feedback for call tracking

CREATE TABLE IF NOT EXISTS voiceprints (
    voiceprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_pesel TEXT NOT NULL,
    voiceprint_hash TEXT,
    voice_embedding TEXT,
    embedding_json TEXT,
    speaker_id TEXT,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sms_verifications (
    verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_pesel TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    status TEXT CHECK (status IN ('pending', 'verified', 'expired')) DEFAULT 'pending',
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    session_id TEXT PRIMARY KEY,
    call_id TEXT UNIQUE,
    patient_pesel TEXT,
    auth_token TEXT,
    sms_code TEXT,
    sms_sent_at TIMESTAMP,
    pesel_verified INTEGER DEFAULT 0,
    sms_verified INTEGER DEFAULT 0,
    voice_verified INTEGER DEFAULT 0,
    voice_confidence REAL,
    voice_verification_status TEXT DEFAULT 'pending' CHECK (voice_verification_status IN ('pending', 'passed', 'failed', 'skipped')),
    voice_similarity_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status TEXT CHECK (status IN ('active', 'expired', 'revoked')) DEFAULT 'active',
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS auth_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT,
    patient_pesel TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('pesel_lookup', 'pesel_verified', 'pesel_failed', 'sms_sent', 'sms_verified', 'sms_failed', 'voice_enrolled', 'voice_verified', 'voice_failed', 'session_created', 'session_revoked', 'auth_failed')),
    status TEXT CHECK (status IN ('success', 'failure', 'warning')),
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_pesel) REFERENCES patients (pesel) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_voiceprints_pesel ON voiceprints (patient_pesel);
CREATE INDEX IF NOT EXISTS idx_sms_verifications_pesel ON sms_verifications (patient_pesel);
CREATE INDEX IF NOT EXISTS idx_sms_verifications_status ON sms_verifications (status);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_pesel ON auth_sessions (patient_pesel);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions (auth_token);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_call_id ON auth_sessions (call_id);
CREATE INDEX IF NOT EXISTS idx_auth_events_pesel ON auth_events (patient_pesel);
CREATE INDEX IF NOT EXISTS idx_auth_events_type ON auth_events (event_type);
