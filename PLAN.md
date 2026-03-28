# VoiceGuard — 4-Hour Implementation Plan

## Team: 4 people | Deadline: 4 hours

---

## What We're Building

A Python package `voiceguard` with:

1. **Clean SDK** — 3-line integration API (idea 1)
2. **JWT verification tokens** — cryptographic proof of identity (idea 2)
3. **Zero-knowledge voice storage** — embeddings only, never raw audio (idea 3)
4. **Live UI** — split-screen: call transcription (left) + agent reasoning/risk panel (right) (ideas 8 + 9)
5. **Demo mode** — simulated attacks, happy path, one-click run (idea 14)
6. **Config-as-code** — YAML config + Docker (idea 15)

---

## Team Assignments

| Person | Role | Focus |
|--------|------|-------|
| **P1** | Backend Core | Python package structure, SDK API, verification pipeline |
| **P2** | Security & Crypto | JWT tokens, audit chain, zero-knowledge embeddings, envelope encryption |
| **P3** | Frontend | React UI — split-screen, WebSocket integration, reasoning panel, risk display |
| **P4** | Integration & Demo | WebSocket server, demo mode, Docker, YAML config, glue between backend and frontend |

---

## Stage 1: Foundation (0:00 – 1:00)

### P1 — Package skeleton

- Create `voiceguard/` Python package structure:
  ```
  voiceguard/
  ├── __init__.py          # exports VerificationSession
  ├── session.py           # VerificationSession class
  ├── otp.py               # OTP generation, hashing, verification
  ├── voice.py             # VoiceVerifier (moved from app/voice_verifier.py)
  ├── pesel.py             # PESEL lookup logic
  ├── models.py            # Pydantic models (VerificationResult, StepStatus, etc.)
  ├── config.py            # Settings loaded from voiceguard.yml
  ├── db.py                # SQLite connection manager
  └── exceptions.py        # Custom exceptions
  ```
- Implement `VerificationSession` with the 3-step flow:
  ```python
  session = VerificationSession(pesel="02211312345")
  session.send_otp()
  session.verify_otp("123456")
  result = session.verify_voice(audio_bytes)
  ```
- Move and refactor existing code from `app/auth_service.py`, `app/voice_verifier.py`, `app/sms.py` into the package
- Each step emits structured events (dict with timestamp, step, status, details) — these feed the UI later

### P2 — Security layer

- Create `voiceguard/crypto/` subpackage:
  ```
  voiceguard/crypto/
  ├── __init__.py
  ├── jwt_tokens.py        # Issue + verify JWT after full auth
  ├── audit_chain.py       # Hash-linked tamper-evident log
  └── embedding_store.py   # Zero-knowledge: store only embeddings, never audio
  ```
- **JWT tokens**: implement `issue_token(session) -> str` and `verify_token(token) -> Claims`
  - Claims: `pesel_verified`, `otp_verified`, `voice_score`, `session_id`, `iat`, `exp`, `jti`
  - HMAC-SHA256 signing with configurable secret
  - Nonce/jti for replay protection
- **Zero-knowledge embedding store**: refactor `voice_verifier.py` to:
  - On enrollment: compute embedding → store 192-dim vector → delete raw audio
  - On verify: compute embedding from live audio → cosine similarity → zero the buffer from memory
  - Add `voiceguard.privacy` with a docstring/comment explaining irreversibility
- **Audit chain**: each event → `SHA-256(prev_hash + event_json)` → stored in `audit_events` table with `prev_hash` column

### P3 — UI scaffold

- Create new React app in `ui/` (or refactor existing):
  ```
  ui/
  ├── src/
  │   ├── App.jsx                # Main layout: split-screen
  │   ├── components/
  │   │   ├── TranscriptPanel.jsx    # Left side: call transcription
  │   │   ├── ReasoningPanel.jsx     # Right side: agent's brain log
  │   │   ├── RiskIndicators.jsx     # Risk score badges (green/yellow/red)
  │   │   ├── StepProgress.jsx       # 3-step progress bar (PESEL → OTP → Voice)
  │   │   └── ConnectionStatus.jsx   # WebSocket connection indicator
  │   ├── hooks/
  │   │   └── useVoiceGuard.js       # WebSocket hook
  │   └── styles/
  │       └── main.css
  ```
- Build the split-screen layout:
  - **Left panel (40%)**: scrolling transcript with timestamps, speaker labels (Agent / User)
  - **Right panel (60%)**: reasoning log + risk indicators at top
- Style: dark theme, monospace for reasoning log, green accent for verified steps, red for flags
- Wire up `useVoiceGuard.js` hook — connects to WebSocket, parses messages, updates state

### P4 — WebSocket server + config

- Create `voiceguard/server/` subpackage:
  ```
  voiceguard/server/
  ├── __init__.py
  ├── ws.py              # WebSocket endpoint (FastAPI)
  ├── events.py          # Event bus: session events → WebSocket broadcast
  └── app.py             # FastAPI app with WS + REST endpoints
  ```
- Implement WebSocket protocol:
  ```
  Server → Client messages:
  {"type": "transcript.add", "speaker": "agent", "text": "...", "ts": "..."}
  {"type": "step.update", "step": "pesel", "status": "verified", "details": {...}}
  {"type": "reasoning.add", "text": "[10:32:01] PESEL lookup → match", "level": "info"}
  {"type": "risk.update", "indicators": {"voice_match": 0.85, "otp_timing": "normal", ...}}
  {"type": "session.complete", "token": "eyJ..."}
  ```
- Create `voiceguard.yml` config loader:
  ```yaml
  verification:
    steps: [pesel, otp, voice]
    voice:
      model: ecapa-tdnn
      threshold: 0.72
      min_audio_seconds: 3
    otp:
      provider: mock
      expiry_seconds: 300
    security:
      max_attempts: 3
      audit: hash_chain
  ui:
    theme: dark
    show_reasoning: true
  ```
- Wire event bus: when `VerificationSession` emits an event → broadcast to all connected WebSocket clients

**Stage 1 checkpoint**: package importable, JWT issuing works, UI renders split-screen with placeholder data, WebSocket connects.

---

## Stage 2: Integration (1:00 – 2:00)

### P1 — Event emission + session manager

- Add event emission to every step in `VerificationSession`:
  - `pesel.lookup_start`, `pesel.verified` / `pesel.failed`
  - `otp.generated` (log that hash is stored, not plaintext), `otp.sent`, `otp.verified` / `otp.failed`
  - `voice.buffer_received` (duration, SNR), `voice.embedding_computed`, `voice.similarity_result`, `voice.verified` / `voice.failed`
- Each event is a dict: `{"ts": ..., "step": ..., "status": ..., "details": {...}, "level": "info|warn|error"}`
- Create `SessionManager` — manages multiple concurrent sessions, routes events to the right WebSocket clients
- Add reasoning text generation: each event gets a human-readable reasoning string
  - Example: `"PESEL 02211312345 → DB lookup → match: Jan Kowalski → phone: +48 600***123 (masked)"`
  - Example: `"OTP generated: 6 digits, SHA-256 hashed before storage, raw code never logged"`
  - Example: `"Voice buffer: 4.2s captured, SNR: 18dB (acceptable) → computing embedding..."`

### P2 — Wire crypto into pipeline

- Integrate JWT issuance at end of successful verification
- Integrate audit chain: every event → append to hash chain in DB
- Integrate zero-knowledge store: make sure `voice.py` never persists raw audio
- Add `voiceguard audit verify` CLI command that walks the chain and reports integrity
- Add risk scoring logic in `voiceguard/risk.py`:
  - `voice_confidence`: cosine similarity score → green (>0.8), yellow (0.72–0.8), red (<0.72)
  - `otp_timing`: time between SMS send and OTP verify → flag if <2s or >300s
  - `attempt_history`: count failed attempts in last hour → flag if >2
  - `overall_risk`: weighted combination → "low" / "medium" / "high"

### P3 — Wire real data into UI

- Connect `useVoiceGuard` hook to real WebSocket server
- `TranscriptPanel`: render incoming `transcript.add` messages as chat bubbles
- `ReasoningPanel`: render `reasoning.add` messages as a scrolling log (monospace, color-coded by level)
- `StepProgress`: update step states from `step.update` messages — animate transitions
- `RiskIndicators`: render from `risk.update` messages:
  - Circular badges: voice confidence %, OTP timing status, attempt count
  - Color-coded: green/yellow/red
  - Tooltip with explanation on hover
- Add smooth animations: steps sliding from grey → yellow (in progress) → green (done) / red (failed)

### P4 — End-to-end flow

- Wire `VerificationSession` events → event bus → WebSocket → UI
- Test full flow manually: start session → PESEL → OTP → voice → see it all in UI
- Create `voiceguard/cli.py` with Click:
  ```
  voiceguard serve          # Start API + WebSocket server + serve UI
  voiceguard demo           # Start in demo mode with simulated data
  voiceguard audit verify   # Verify audit chain integrity
  ```
- Start building demo mode: pre-scripted sessions that play through automatically

**Stage 2 checkpoint**: full pipeline works end-to-end. Type PESEL → see it in UI reasoning panel. Send OTP → see hash event. Voice verify → see score + risk indicators. JWT token displayed at end.

---

## Stage 3: Demo Mode + Polish (2:00 – 3:00)

### P1 — Demo scenarios

- Create `voiceguard/demo/` with pre-scripted scenarios:
  ```
  voiceguard/demo/
  ├── __init__.py
  ├── runner.py            # Scenario runner with timing
  ├── scenarios/
  │   ├── happy_path.py    # Normal verification, all green
  │   ├── wrong_voice.py   # Different person's voice → mismatch → red
  │   ├── replay_attack.py # Recorded audio → (future: anti-spoof flag) → suspicious
  │   └── brute_force.py   # Rapid OTP attempts → rate limit → lockout
  ```
- Each scenario is a sequence of timed events that simulate a real session
- `runner.py` plays events with realistic delays (1-3s between steps) and pushes them through the same event bus → WebSocket → UI
- Happy path: PESEL verified → OTP sent → OTP verified → voice score 0.85 → all green → JWT issued
- Wrong voice: PESEL verified → OTP verified → voice score 0.41 → RED → "Voice mismatch detected" → session rejected
- Brute force: 3 rapid OTP attempts with wrong codes → progressive lockout → "Session locked after 3 failed attempts"

### P2 — Security polish

- Make sure OTP codes are **never** logged in plaintext anywhere — only SHA-256 hash in reasoning panel
- Add memory zeroing after voice embedding comparison (Python: overwrite bytes, del references)
- Review all event details for PII leakage — mask phone numbers, truncate PESEL in logs
- Add `voiceguard audit export --format json` for compliance export
- Write security notes in README: threat model, what we protect against, what's out of scope

### P3 — UI polish

- Add header bar: "VoiceGuard" logo/text + session ID + connection status dot
- Add scenario selector dropdown (for demo mode): "Happy Path", "Wrong Voice", "Brute Force OTP"
- Animate risk indicators: pulse animation when values change, smooth color transitions
- Add "Session Complete" overlay: green checkmark + JWT token (truncated, copyable) OR red X + rejection reason
- Make reasoning panel auto-scroll to bottom, with manual scroll-lock if user scrolls up
- Responsive: works on a projector (1920x1080) — this is for the live demo

### P4 — Docker + packaging

- Create `Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  COPY . /app
  WORKDIR /app
  RUN pip install -e .
  RUN cd ui && npm install && npm run build
  EXPOSE 8000
  CMD ["voiceguard", "serve", "--host", "0.0.0.0"]
  ```
- Create `docker-compose.yml` with single service
- Create `setup.py` / `pyproject.toml` for pip-installable package
- Create `voiceguard.yml.example` with sensible defaults
- Test: `pip install -e .` → `voiceguard demo` → opens browser → scenarios play

**Stage 3 checkpoint**: `voiceguard demo` runs, shows 3 scenarios in the UI. All security measures in place. Docker builds.

---

## Stage 4: Final Polish + Presentation Prep (3:00 – 4:00)

### P1 — README + API docs

- Write `README.md` for the package:
  - What it is (1 paragraph)
  - Quick start (5 lines)
  - Architecture diagram (ASCII)
  - Security model (bullet points: zero-knowledge, JWT, audit chain, rate limiting)
  - Configuration reference
- Add inline code comments on the non-obvious parts (crypto, embedding math)
- Final code review: clean up dead code, make sure imports are clean

### P2 — Live attack demo prep

- Prepare talking points for each scenario:
  - Happy path: "Here's a normal verification — 3 steps, 15 seconds, JWT issued"
  - Wrong voice: "Now someone steals PESEL and OTP — but voice doesn't match, rejected"
  - Brute force: "Automated attack trying OTP codes — rate limiter kicks in after 3 attempts"
- Make sure audit chain verification works as a live CLI demo: `voiceguard audit verify` → "Chain intact, 47 events, no tampering detected"
- Test JWT: decode it live in jwt.io to show claims to judges

### P3 — UI final touches

- Add subtle animations for demo wow factor
- Test on projector resolution
- Add "Powered by VoiceGuard" footer
- Screenshot/record a backup video in case live demo fails
- Make sure scenario selector is obvious and works with single click

### P4 — Integration testing + backup plan

- Run full end-to-end test: Docker build → `voiceguard demo` → all 3 scenarios → verify
- Test `pip install -e .` from clean virtualenv
- Prepare backup: if Docker fails, `python -m voiceguard.server.app` works directly
- Prepare backup: if WebSocket fails, UI has a "replay from file" mode that reads saved events
- Final check: does `voiceguard serve` + `voiceguard demo` both work?

---

## Deliverables Checklist

- [ ] `voiceguard` Python package, pip-installable
- [ ] 3-line API: `VerificationSession` with PESEL → OTP → Voice flow
- [ ] JWT tokens issued after successful verification
- [ ] Zero-knowledge voice storage (embeddings only)
- [ ] Hash-linked audit chain with CLI verification
- [ ] Risk scoring (voice confidence, OTP timing, attempt count)
- [ ] WebSocket streaming protocol
- [ ] Split-screen UI: transcript (left) + reasoning + risk (right)
- [ ] Demo mode with 3 scenarios (happy path, wrong voice, brute force)
- [ ] `voiceguard.yml` config file
- [ ] Docker deployment
- [ ] README with quick start + security model

---

## Key Decisions

- **No appointment scheduling** — we cut all hospital/booking logic. This is a verification package only.
- **SQLite stays** — good enough for demo, no need for Postgres complexity.
- **Mock SMS by default** — Twilio is optional. Demo mode uses mock.
- **SpeechBrain ECAPA-TDNN stays** — proven model, already integrated.
- **Anti-spoofing (idea 4) is deferred** — if we finish early, P2 adds basic spectral analysis. Not in the 4-hour plan.
