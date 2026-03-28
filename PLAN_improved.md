# Database-Backed Voice Scheduling Agent — Improved Architecture Plan

## Goal

Build a voice scheduling system where:

1. The caller is identified and authenticated.
2. The agent checks real doctor availability from the database.
3. The caller confirms a slot.
4. The booking is persisted to the database.

This keeps the database as the system of record and treats voice verification as one part of the workflow, not the entire product.

---

## Core Product Shape

The system has 3 layers:

1. Database layer
2. Business logic and tools layer
3. Voice agent and demo/UI layer

The correct dependency direction is:

`Voice/UI -> Tools/Services -> SQLite`

The voice model should never be the source of truth for identity, availability, or booking state. It should only orchestrate tool calls.

---

## 1. Database Layer

SQLite remains the source of truth for all operational state.

### Required tables

- `patients`
  - PESEL
  - full name
  - phone number
  - verification ZIP
  - optional enrolled voice sample reference

- `doctors`
  - doctor id
  - full name
  - specialty

- `appointments`
  - appointment id
  - doctor id
  - patient PESEL
  - appointment datetime
  - status (`Available` / `Booked`)

- `voiceprints`
  - patient PESEL
  - embedding or hash metadata
  - model info

- `auth_sessions`
  - session id
  - call id
  - patient PESEL
  - PESEL verification status
  - SMS verification status
  - voice verification status
  - timestamps and expiry

- `auth_events`
  - audit trail of verification and session events

### Principle

All reads and writes that matter to the product must land in SQLite.

Examples:

- patient lookup
- doctor lookup
- appointment availability
- booking confirmation
- auth session status
- voice verification result

---

## 2. Business Logic Layer

This is where the real application logic lives. It should be deterministic and testable without a live model.

### A. Scheduling service

Owns:

- patient lookup
- doctor lookup
- availability search
- booking updates

Example responsibilities:

- normalize doctor names and specialties
- resolve fuzzy doctor references safely
- verify a slot is still available before booking
- write confirmed bookings transactionally

### B. Authentication service

Owns:

- PESEL verification
- SMS sending and verification
- voice verification
- auth session state transitions

Example responsibilities:

- create or update `auth_sessions`
- write `auth_events`
- gate access to scheduling tools until auth conditions are met

### C. Tool registry

This is the boundary the live agent uses.

Recommended tool groups:

- Identity tools
  - `verify_patient_identity`
  - `send_sms`
  - `verify_sms`
  - `get_auth_status`

- Voice/auth tools
  - `start_voice_check`
  - `get_voice_status`

- Scheduling tools
  - `find_doctor_availability`
  - `book_appointment`

### Principle

The live model calls tools. Tools call services. Services read and write the database.

---

## 3. Voice Agent Layer

This layer is Gemini Live, Vapi, or another realtime voice interface.

### Responsibilities

- talk to the caller
- collect missing information
- decide which tool to call
- summarize tool outputs back to the caller

### Non-responsibilities

The model should not:

- invent patient records
- invent doctors
- invent availability
- confirm bookings without a successful tool response
- treat its own memory as state

### Required conversational flow

1. Ask who the patient is and collect PESEL.
2. Verify PESEL and ZIP.
3. Trigger SMS and voice verification if required.
4. Only after auth passes, ask for doctor or specialty.
5. Query availability from the database.
6. Ask the caller to confirm one exact slot.
7. Call `book_appointment`.
8. Confirm the booking only if the tool returns success.

---

## Recommended System Modules

Use this structure conceptually, whether or not the code is packaged exactly this way:

```text
database/
  schema.sql
  client.py
  seed_data.py

services/
  scheduling_service.py
  auth_service.py
  voice_service.py

agent/
  tool_registry.py
  gemini_live_config.py
  prompting.py

voiceguard/
  jwt_tokens.py
  audit_chain.py
  embedding_store.py
  risk.py

server/
  api.py
  ws.py
  events.py

ui/
  ...
```

The key point is that `voiceguard` should be a subsystem for auth/security, not the whole application.

---

## What From the Original Plan Should Stay

These ideas are still useful:

- JWT or signed auth result after successful verification
- audit chain for security-sensitive events
- zero-knowledge voice embedding storage
- split-screen live UI for transcript and reasoning
- demo scenarios for happy path and attack path
- config-as-code and Docker

---

## What Should Change From the Original Plan

### Do not make verification the whole product

The original plan treats the system like a generic verification SDK. That is too detached from the actual hospital scheduling use case.

### Do not remove scheduling

Scheduling is not optional. It is the core business function. Authentication only exists to protect access to that function.

### Do not let the model hold business state

The DB must remain authoritative for:

- who the patient is
- which doctors exist
- what slots are available
- what is already booked

---

## Recommended Demo Narrative

For a hackathon/demo, the strongest story is:

1. Caller starts a medical scheduling call.
2. System verifies PESEL + SMS + background voice match.
3. Agent checks real database availability.
4. Caller picks a slot.
5. Booking is written into SQLite.
6. UI shows transcript, auth state, risk indicators, and booking result.

That is stronger than a verification-only demo because it shows both security and business outcome.

---

## Implementation Order

### Phase 1

Stabilize backend truth:

- finalize SQLite schema
- finalize seed data
- finalize scheduling service
- finalize auth service

### Phase 2

Stabilize tool contract:

- define tool schemas clearly
- handle model argument variation robustly
- make tool calls idempotent where possible

### Phase 3

Stabilize live agent:

- connect Gemini Live or Vapi
- enforce prompt rules
- ensure tool-only state transitions

### Phase 4

Add demo and observability:

- transcript stream
- reasoning and risk panel
- session audit log
- happy path and attack path demos

---

## Final Architecture Decision

The correct top-level architecture is:

**Database-backed scheduling application with VoiceGuard-style authentication**

Not:

**Standalone verification SDK with no scheduling**

That means:

- SQLite stays central
- scheduling stays central
- auth is a gate in front of scheduling
- the live model is an orchestrator over tool calls

