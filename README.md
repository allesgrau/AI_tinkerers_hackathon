# VoiceGuard

**Multi-factor voice identity verification for healthcare.**

VoiceGuard is a Python package that verifies patient identity through three factors:

1. **PESEL + ZIP code** -- patient lookup against a hospital database
2. **SMS one-time code** -- 6-digit OTP sent via Twilio, SHA-256 hashed
3. **Speaker voice biometrics** -- ECAPA-TDNN embeddings (SpeechBrain) compared via cosine similarity

All verification events are logged to a tamper-evident hash-chain audit trail, and a signed JWT token is issued on successful authentication.

---

## Quick Start

```bash
# Install from GitHub
pip install git+https://github.com/allesgrau/AI_tinkerers_hackathon.git

# Start the server
voiceguard serve
```

Open **http://localhost:8000** in your browser.

---

## Two Interfaces

| Interface | URL | Description |
|-----------|-----|-------------|
| **Landing page** | `/` | Choose which interface to use |
| **Live Verification** | `/verify` | Interactive 3-step verification: speak your PESEL, receive SMS code, verify your voice |
| **Ops Dashboard** | `/dashboard` | Real-time monitoring console with transcripts, tool calls, reasoning traces, and risk indicators |

### Live Verification (`/verify`)

The verification page lets you:

- **Enroll** your voice (record 5+ seconds to create a voiceprint)
- **Verify** your identity (PESEL -> SMS code -> voice match)

Microphone access is required. The page uses the Web Speech API for speech recognition and MediaRecorder for voice capture.

### Ops Dashboard (`/dashboard`)

A React-based real-time monitoring console that shows:

- Live call transcripts (caller + agent)
- Tool call activity and results
- Backend reasoning traces
- Risk indicators and session state
- Voice activity visualization

To run the dashboard in development mode:

```bash
npm install
npm run dev
```

This starts Vite on port 5173 with API proxy to the backend on port 8000.

---

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Twilio SMS (for OTP delivery)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
SMS_PROVIDER=twilio

# Optional
GEMINI_LIVE_MODEL=models/gemini-3.1-flash-live-preview
GEMINI_LIVE_VOICE=Zephyr
PUBLIC_BASE_URL=https://your-tunnel-url
```

---

## Architecture

```
voiceguard/
  server/           FastAPI app, WebSocket events, static pages
  crypto/            Embedding store, JWT tokens, audit chain
  demo/              Simulated verification scenarios
  voice.py           Speaker verification (ECAPA-TDNN)
  otp.py             OTP generation + SHA-256 hashing
  pesel.py           PESEL format validation
  session.py         Verification session orchestrator
  risk.py            Risk assessment scoring

agent/               Gemini Live voice agent + scheduling tools
app/                 Twilio bridge, call registry, SMS service
database/            SQLite schema + seed data
ui_2/                React ops dashboard (Vite)
```

### Verification Pipeline

```
Caller -> PESEL lookup -> OTP via SMS -> Voice embedding match -> JWT issued
              |                |                  |                    |
          patients DB     SHA-256 hash     cosine similarity     hash-chain
                          + Twilio SMS     vs enrolled print     audit log
```

### Security

- OTP codes are SHA-256 hashed before storage (plaintext never persisted)
- Voice embeddings stored as 192-dim vectors; raw audio is never saved
- JWT tokens include nonce-based replay prevention
- All session events recorded in a tamper-evident hash chain
- Risk scoring combines voice confidence, OTP timing, and attempt count

---

## Database

SQLite database (`hospital_agent.db`) with tables for patients, doctors, appointments, voiceprints, SMS verifications, auth sessions, and audit events.

### Test Patients

| Name | PESEL | ZIP |
|------|-------|-----|
| John Smith | 02211312345 | 10001 |
| Mary Johnson | 83051298765 | 10002 |
| Peter Miller | 99123145678 | 10003 |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/enroll/voice` | POST | Enroll voice (audio -> embedding -> DB) |
| `/api/verify/pesel` | POST | Verify PESEL against patient DB |
| `/api/verify/otp/send` | POST | Generate and send OTP via SMS |
| `/api/verify/otp/verify` | POST | Verify OTP code |
| `/api/verify/voice` | POST | Verify voice against enrolled embedding |
| `/api/verify/status` | POST | Get session verification state |
| `/ws` | WebSocket | Real-time event stream |
| `/health` | GET | Health check |

---

## CLI Commands

```bash
voiceguard serve              # Start the server
voiceguard serve --port 9000  # Custom port
voiceguard demo               # Run with simulated scenarios
voiceguard audit verify <id>  # Verify audit chain integrity
voiceguard audit export <id>  # Export audit chain as JSON
```

---

## License

Hackathon project -- AI Tinkerers 2026.
