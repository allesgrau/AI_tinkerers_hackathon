# 🏥 Hospital Voice Auth Agent - Setup Guide

## Overview
This is a **production-ready voice authentication system** for hospitals/clinics. Real code, no mockups!

**Tech Stack:**
- FastAPI (REST API)
- SQLite (database)
- Twilio (SMS provider)
- SpeechBrain (voice biometrics - ML model)
- Vapi (voice agent platform)
- Docker (containerized)

---

## 🔑 API Keys Required

### 1. **Twilio** (SMS OTP)
Get from: https://www.twilio.com/console

Required:
- `TWILIO_ACCOUNT_SID` - Your account ID
- `TWILIO_AUTH_TOKEN` - Your auth token  
- `TWILIO_FROM_NUMBER` - Phone number to send SMS from (e.g., +1234567890)

### 2. **Vapi** (Voice Agent Platform)
Get from: https://vapi.ai

Required:
- `VAPI_API_KEY` - API key for Vapi
- `VAPI_PHONE_NUMBER` - Phone number for voice calls (e.g., +48123456789)

### 3. **Google Cloud** (Optional - for Vertex AI)
⚠️ **CURRENTLY USING: SpeechBrain** (ML model runs offline, no API key needed!)

If you want to use Google Vertex AI instead:
- Download Google Cloud credentials JSON
- Set `GOOGLE_APPLICATION_CREDENTIALS` path

---

## 🚀 Quick Start

### Option 1: Local Setup (Python)

#### 1. Clone & Setup
```bash
git clone <repo>
cd AI_tinkerers_hackathon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your editor
```

Example `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
VAPI_API_KEY=your_vapi_key
VAPI_PHONE_NUMBER=+48123456789
```

#### 3. Setup Database
```bash
# Create database with schema + seed data
python scripts/setup_database.py
```

#### 4. Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Running at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs (Swagger UI)

---

### Option 2: Docker Setup (Recommended for Production)

#### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### 2. Build & Run
```bash
# Build image
docker compose build

# Run container
docker compose up -d

# Setup database
docker compose exec hospital-agent-api python scripts/setup_database.py

# View logs
docker compose logs -f
```

**API Running at:** http://localhost:8000

#### 3. Stop
```bash
docker compose down
```

---

## 📋 API Endpoints

### Health Check
```bash
GET /health
```

### 1. Verify PESEL (Step 1)
```bash
POST /vapi/tools/collect-pesel
{
  "call_id": "call_12345",
  "pesel": "12345678901"
}

Response:
{
  "ok": true,
  "patient": {
    "pesel": "12345678901",
    "full_name": "Jan Kowalski",
    "phone_number": "+48501111222"
  }
}
```

### 2. Send SMS OTP (Step 2)
```bash
POST /vapi/tools/send-sms
{
  "call_id": "call_12345"
}

Response:
{
  "ok": true,
  "message": "Kod SMS został wysłany...",
  "provider_result": "Twilio SID: SMxxxxxxx"
}
```

### 3. Verify SMS Code (Step 2b)
```bash
POST /vapi/tools/verify-sms
{
  "call_id": "call_12345",
  "code": "123456"
}

Response:
{
  "ok": true,
  "message": "Kod SMS poprawny."
}
```

### 4. Upload & Process Audio (Step 3)
```bash
POST /vapi/media/audio
{
  "call_id": "call_12345",
  "audio_base64": "UklGRi4AAABXQU1F...",  # WAV file encoded
  "extension": "wav"
}

Response:
{
  "ok": true,
  "audio_path": "/app/audio_buffer/call_12345.wav",
  "size_bytes": 1024
}
```

### 5. Get Auth Status
```bash
POST /vapi/tools/auth-status
{
  "call_id": "call_12345"
}

Response:
{
  "ok": true,
  "call_id": "call_12345",
  "patient_pesel": "12345678901",
  "patient_name": "Jan Kowalski",
  "sms_verified": true,
  "voice_verification_status": "passed",
  "voice_similarity_score": 0.92,
  "fully_authenticated": true
}
```

---

## 🔐 Authentication Flow

```
User Calls → Vapi → API
    ↓
1️⃣  PESEL Lookup
    - ✅ Verify PESEL format
    - ✅ Check patient in database
    
    ↓
2️⃣  SMS OTP Verification
    - ✅ Generate random 6-digit code
    - ✅ Send via Twilio (real SMS!)
    - ✅ User reads code to agent
    - ✅ Verify code matches
    
    ↓
3️⃣  Voice Biometrics (SpeechBrain ML)
    - ✅ Record voice sample
    - ✅ Extract voice embedding (offline)
    - ✅ Compare with stored voiceprint
    - ✅ Return similarity score (0-1)
    
    ↓
4️⃣  Create Session
    - ✅ All 3 steps passed
    - ✅ User fully authenticated
    - ✅ Session active for 1 hour
```

---

## 📊 Database Schema

### Key Tables

| Table | Purpose |
|-------|---------|
| `patients` | Patient records (PESEL, name, phone) |
| `doctors` | Doctor information |
| `appointments` | Appointment slots |
| `auth_sessions` | Active call sessions (call_id, verification status) |
| `sms_verifications` | OTP tracking |
| `voiceprints` | Voice biometric embeddings |
| `auth_events` | Audit log (all auth events) |

---

## 🔍 Monitoring & Logs

### View Auth Events
```sql
-- See all auth events for a patient
SELECT * FROM auth_events 
WHERE patient_pesel = '12345678901' 
ORDER BY created_at DESC;

-- See failed attempts
SELECT * FROM auth_events 
WHERE status = 'failure' 
ORDER BY created_at DESC;
```

### View Active Sessions
```sql
SELECT * FROM auth_sessions 
WHERE voice_verification_status = 'pending' 
ORDER BY created_at DESC;
```

### View Logs
```bash
# Local
tail -f /tmp/hospital-agent.log

# Docker
docker compose logs -f hospital-agent-api
```

---

## ⚙️ Configuration

### Voice Similarity Threshold
Default: `0.72` (72% confidence required)

Edit in `.env`:
```
VOICE_SIMILARITY_THRESHOLD=0.72
```

Lower = More lenient (more false positives)  
Higher = More strict (more false negatives)

### SMS Provider
Currently: `twilio`

To use mock SMS for testing:
```
SMS_PROVIDER=mock
```

This will print OTP to console instead of sending.

---

## 🐛 Troubleshooting

### "Module not found: app"
```bash
# Make sure you're running from project root
cd AI_tinkerers_hackathon
python -m uvicorn app.main:app --reload
```

### "Twilio credentials not found"
```bash
# Check .env file exists and has:
TWILIO_ACCOUNT_SID=ACxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
```

### "No module named 'speechbrain'"
```bash
# Re-install requirements
pip install --upgrade -r requirements.txt

# Or just install missing
pip install speechbrain torch torchaudio
```

### "Audio buffer not writable"
```bash
# Make sure directory exists
mkdir -p audio_buffer
chmod 755 audio_buffer
```

---

## 📚 Project Structure

```
AI_tinkerers_hackathon/
├── app/
│   ├── main.py              # FastAPI routes
│   ├── auth_service.py      # Authentication logic (Person 4 + Person 1)
│   ├── voice_verifier.py    # Voice biometrics (SpeechBrain)
│   ├── sms.py               # SMS provider (Twilio)
│   ├── audit_logger.py      # Audit logging
│   ├── config.py            # Configuration
│   └── db.py                # Database helpers
├── database/
│   ├── schema.sql           # Database schema
│   └── seed_data.py         # Sample data
├── scripts/
│   ├── setup_database.py    # Initialize DB
│   └── test_auth_flow.py    # Demo script
├── docker-compose.yml       # Docker setup
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 👥 Team Roles

| Person | Role | Focus |
|--------|------|-------|
| 👤 Person 1 | Voice + Vapi | Voice agent, call routing |
| 👤 Person 2 | Backend | Cloud Functions, API, prompt generation |
| 👤 Person 3 | UI/Panel | React dashboard, configuration UI |
| 👤 **Person 4** | **Auth + Integrations** | **PESEL, SMS, Voice Biometrics, Security** |

---

## 📝 Notes

- ✅ **Real Code** - Production-ready (no mockups!)
- ✅ **Real SMS** - Twilio integration (not console logging)
- ✅ **Real Voice** - SpeechBrain ML model (offline, no API needed)
- ✅ **Real Security** - Audit logging, error tracking
- ✅ **Dockerized** - Easy deployment
- ⏳ **Vapi Integration** - Ready for Person 1

---

**Status**: Phase 0-1 ✅  
**Last Updated**: 2026-03-28
