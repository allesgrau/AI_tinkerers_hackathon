# Authentication System - Person 4 (Auth + Integracje)

## Overview

This is the authentication & integration layer for the voice scheduling agent. Handles:
- PESEL patient verification (lookup)
- SMS OTP verification (Twilio/Switch)
- Voice biometrics enrollment & verification (Vertex AI)
- Session management & token validation
- Audit logging

## Current Status - Phase 0

✅ **Database schema** with auth tables
✅ **Mock integrations** (SMS, voice biometrics)
✅ **Core auth service** with 3-step flow
✅ **Test demo** showing complete auth flow
⏳ **Real API integrations** (to be implemented in Phase 1/2)

## Database Schema

### Tables Created

```sql
voiceprints          -- Store patient voice profiles
sms_verifications    -- Track OTP codes and verification status
auth_sessions        -- Active authenticated sessions
auth_events          -- Audit log of all auth events
```

See `database/schema.sql` for full definitions.

## How It Works - 3-Step Auth Flow

### Step 1: PESEL Verification
```python
success, message = auth.verify_pesel("12345678901")
# Returns: (True, "Jan Kowalski") or (False, "Patient not found")
```

### Step 2: SMS OTP
```python
# Send OTP
success, msg = auth.send_sms_otp("12345678901")
# Mock: Prints OTP to console
# Real: Sends via Twilio/Switch

# Verify OTP
success, msg = auth.verify_sms_code("12345678901", "123456")
```

### Step 3: Voice Biometrics

**First time:** Enroll voice
```python
success, msg = auth.enroll_voice("12345678901", voice_data)
# Stores voiceprint in DB
```

**Subsequent calls:** Verify voice
```python
success, details = auth.verify_voice("12345678901", voice_data)
# Returns: (True, {"confidence": 0.92}) or (False, {...})
```

### Step 3b: Create Session
```python
success, token = auth.create_auth_session(
    pesel="12345678901",
    pesel_verified=True,
    sms_verified=True,
    voice_verified=True,
    voice_confidence=0.92
)
# Returns: (True, "<long_token_string>")
```

### Step 3c: Verify Token
```python
is_valid, pesel = auth.verify_auth_token(token)
# Returns: (True, "12345678901") or (False, None)
```

## Testing

Run the complete auth flow demo:
```bash
python scripts/test_auth_flow.py
```

This will:
1. ✅ Verify PESEL for a test patient
2. ✅ Send & verify SMS OTP
3. ✅ Enroll voice
4. ✅ Verify voice
5. ✅ Create and verify auth session

## API Contracts (for Person 2 - Backend)

Person 2 (Backend) needs to implement these endpoints in Cloud Functions:

### 1. POST /auth/verify-pesel
Check if patient exists in system
```json
// Request
{
  "pesel": "12345678901"
}

// Success Response
{
  "success": true,
  "patient_name": "Jan Kowalski",
  "message": "PESEL verified"
}

// Failure Response
{
  "success": false,
  "error": "Patient not found"
}
```

### 2. POST /auth/send-sms
Send OTP code to patient's phone
```json
// Request
{
  "pesel": "12345678901"
}

// Response
{
  "success": true,
  "message": "OTP sent to +48501111222"
}
```

### 3. POST /auth/verify-sms
Verify OTP code entered by user
```json
// Request
{
  "pesel": "12345678901",
  "otp_code": "123456"
}

// Success Response
{
  "success": true,
  "message": "SMS verified successfully"
}

// Failure Response
{
  "success": false,
  "error": "Wrong OTP code"
}
```

### 4. POST /auth/enroll-voice
Enroll patient's voice (first time)
```json
// Request
{
  "pesel": "12345678901",
  "voice_data": "<base64_encoded_audio>"
}

// Response
{
  "success": true,
  "message": "Voice enrolled successfully"
}
```

### 5. POST /auth/verify-voice
Verify voice on subsequent calls
```json
// Request
{
  "pesel": "12345678901",
  "voice_data": "<base64_encoded_audio>"
}

// Success Response
{
  "success": true,
  "confidence": 0.92,
  "message": "Voice verified (92% confidence)"
}

// Failure Response
{
  "success": false,
  "confidence": 0.45,
  "error": "Voice does not match (45% confidence)"
}
```

### 6. POST /auth/create-session
Create authenticated session after all 3 steps pass
```json
// Request
{
  "pesel": "12345678901",
  "pesel_verified": true,
  "sms_verified": true,
  "voice_verified": true,
  "voice_confidence": 0.92
}

// Response
{
  "success": true,
  "auth_token": "b505ea8c7472be23944247d64a3fd041...",
  "expires_in": 3600
}
```

### 7. POST /auth/verify-token
Verify auth token (used by Agent in subsequent calls)
```json
// Request
{
  "auth_token": "b505ea8c7472be23944247d64a3fd041..."
}

// Success Response
{
  "success": true,
  "patient_pesel": "12345678901"
}

// Failure Response
{
  "success": false,
  "error": "Invalid or expired token"
}
```

## Mock Integrations

Currently using mock implementations:

### Mock SMS
```python
class MockSMSProvider:
    # Prints OTP to console instead of sending
    # To integrate with Twilio: replace send_sms() implementation
```

### Mock Voice Biometrics
```python
class MockVoiceBiometrics:
    # Generates random confidence (60-99%)
    # To integrate with Vertex AI: replace enroll_voice() and verify_voice()
```

## Real Integrations (Future - Phase 1/2)

### Twilio / Switch (SMS)
```python
# When Person 4 gets API key:
# 1. Replace MockSMSProvider with TwilioSMSProvider
# 2. Add API key to environment
# 3. Implement actual SMS sending
```

### Google Vertex AI (Voice Biometrics)
```python
# When Person 4 sets up Vertex AI:
# 1. Replace MockVoiceBiometrics with VertexAIBiometrics
# 2. Configure authentication
# 3. Implement voice enrollment & verification
```

### Auth0 (Future - multi-tenant)
```python
# For phase 2 when supporting multi-tenant:
# Integrate Auth0 tenant management
```

## Database Queries

### View auth events for a patient
```sql
SELECT * FROM auth_events WHERE patient_pesel = '12345678901' ORDER BY created_at DESC;
```

### View active sessions
```sql
SELECT * FROM auth_sessions WHERE status = 'active' AND expires_at > CURRENT_TIMESTAMP;
```

### View enrolled voiceprints
```sql
SELECT patient_pesel, speaker_id, created_at FROM voiceprints;
```

## File Structure

```
auth/
├── __init__.py              # Package marker
└── auth_service.py          # Core AuthService class
                            # Mock SMS & Voice providers
                            # API contracts documentation

scripts/
├── setup_database.py        # Creates tables & seeds data
└── test_auth_flow.py       # Test demo of complete flow

database/
└── schema.sql              # All table definitions
```

## Notes for Phase 1/2

- Mock SMS currently prints to console - needs Twilio integration
- Mock voice returns random confidence (60-99%) - needs Vertex AI integration
- Auth0 tenant management - not yet implemented
- Rate limiting & security hardening - to be added
- Input validation & sanitization - to be enhanced

---

**Person 4 Contact**: Auth + Integracije
**Status**: Phase 0 ✅
**Next**: Phase 1 - Core building (integrate real APIs)
