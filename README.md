# VoiceGuard

**Multi-factor voice identity verification — as a Python package.**

```bash
pip install git+https://github.com/allesgrau/AI_tinkerers_hackathon.git
voiceguard serve
```

That's it. Open `http://localhost:8000` and you have a full identity verification pipeline running.

---

## The Problem

Every day, hospitals, banks, and government offices handle thousands of sensitive phone calls. The caller says "I'm Jan Kowalski, I need my test results." The agent has no way to truly verify that. Current solutions are either insecure (knowledge-based questions anyone can Google) or unusable (long IVR menus that make people hang up).

Voice AI agents are coming to these institutions fast — but **without real identity verification, they're a liability, not an asset.**

## Our Solution

VoiceGuard adds multi-layer identity verification to any voice agent in three lines of integration. The caller talks naturally while being verified through:

1. **PESEL + ZIP code** — instant database lookup against patient/citizen records
2. **SMS one-time code** — cryptographic OTP sent via Twilio, SHA-256 hashed (never stored in plaintext)
3. **Speaker voice biometrics** — ECAPA-TDNN neural embeddings (SpeechBrain) compared via cosine similarity against an enrolled voiceprint

Only after all three factors pass does the agent unlock sensitive actions (booking appointments, sharing medical results, processing requests). A signed JWT token is issued and every step is logged to a **tamper-evident hash-chain audit trail** — critical for healthcare and financial compliance.

## Why This Matters

| Sector | Problem today | With VoiceGuard |
|--------|--------------|-----------------|
| **Healthcare** | Phone agents can't verify callers, so they can't share results or book appointments | Verified caller gets full self-service in a natural conversation |
| **Banking** | Knowledge-based auth is insecure; fraudsters social-engineer their way in | Voice biometrics + OTP = fraud-resistant, hands-free auth |
| **Government** | Citizens wait on hold for identity checks that take minutes | Automated 3-factor verification in seconds |

This isn't a future problem — it's happening now. As institutions deploy voice AI agents, the identity gap becomes a blocker. VoiceGuard removes that blocker.

## What Makes This Different

**It's a package, not a platform.** Most identity verification solutions are heavyweight SaaS products with enterprise sales cycles. VoiceGuard is a `pip install` that any developer can drop into their existing voice agent. The verification pipeline runs locally, voice embeddings stay on your infrastructure, and the audit chain is in your own SQLite database.

**It combines conversation with security.** The caller doesn't navigate menus or press buttons — they just talk. The system listens for their PESEL, sends an SMS, and matches their voice, all within the natural flow of conversation.

**It's built for compliance.** Every verification step produces a cryptographic audit event linked in an immutable hash chain. Regulators can verify the chain's integrity with one CLI command: `voiceguard audit verify <session-id>`.

---

## Architecture

```
Caller ──> Gemini Live (conversation) ──> FastAPI (orchestration)
                                              |
                    ┌─────────────────────────┼─────────────────────────┐
                    |                         |                         |
              PESEL lookup              Twilio SMS OTP          SpeechBrain voice
              (SQLite)                  (SHA-256 hashed)        (ECAPA-TDNN, 192-dim)
                    |                         |                         |
                    └─────────────────────────┼─────────────────────────┘
                                              |
                                     JWT token issued
                                     Hash-chain audit log
```

**Stack:** Google Gemini Live | FastAPI | Twilio SMS | SpeechBrain | SQLite | React

---

## Two Interfaces

| | URL | What it does |
|---|---|---|
| **Live Verification** | `/verify` | Interactive demo — enroll your voice, then go through the full 3-step verification with your microphone |
| **Ops Dashboard** | `/dashboard` | Real-time monitoring: transcripts, tool calls, reasoning traces, risk scores, session state |

---

## Honest Note

We pivoted mid-hackathon. The code has rough edges and the end-to-end flow isn't bulletproof — we know that. But as a team of 2 undergrads and 2 master's students, we're proud of what we built in the time we had. We discovered some incredible tools (Gemini Live, SpeechBrain, Claude Code) and we genuinely plan to keep working on this after the hackathon because the problem is real and the solution is viable.

What works: the verification pipeline, the audit chain, the voice enrollment, the SMS delivery, the package structure, and the monitoring dashboard. What needs more time: hardening the Twilio call integration and polishing the browser-to-agent flow.

We had a blast building this. Thanks for reading.

---

## Quick Reference

```bash
# Install
pip install git+https://github.com/allesgrau/AI_tinkerers_hackathon.git

# Run
voiceguard serve

# CLI
voiceguard serve --port 9000      # custom port
voiceguard demo                    # simulated scenarios
voiceguard audit verify <id>       # verify audit chain integrity
voiceguard audit export <id>       # export audit trail as JSON
```

### API

| Endpoint | Purpose |
|----------|---------|
| `POST /api/enroll/voice` | Enroll speaker voiceprint |
| `POST /api/verify/pesel` | PESEL + ZIP verification |
| `POST /api/verify/otp/send` | Send SMS OTP |
| `POST /api/verify/otp/verify` | Verify OTP code |
| `POST /api/verify/voice` | Speaker voice match |
| `GET /ws` | Real-time event stream |

### Configuration

Copy `.env.example` to `.env`:

```env
GEMINI_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890
SMS_PROVIDER=twilio
```

---

*Built at AI Tinkerers Hackathon 2026.*
