# Dependency Architecture Plan

## Goal

Split the system into:

1. A reusable dependency package: `voiceguard`
2. A host application that owns the business database and scheduling logic

This allows another project to import `voiceguard` and use it with its own database implementation.

---

## High-Level Architecture

The correct split is:

`Host App -> voiceguard package`

Not:

`voiceguard package -> Host App`

The host app remains responsible for:

- business entities
- database schema
- scheduling logic
- external agent integration

The `voiceguard` package becomes a reusable verification/auth toolkit.

---

## What Goes Into `voiceguard`

`voiceguard` should contain reusable logic that is independent of a specific hospital schema.

### Good candidates

- verification state machine
- PESEL validation helpers
- OTP generation and verification logic
- voice verification logic
- JWT issuance and verification
- risk scoring
- audit-chain utilities
- config loading
- common exceptions
- typed result models

### Example package structure

```text
voiceguard/
  __init__.py
  session.py
  models.py
  exceptions.py
  config.py
  pesel.py
  otp.py
  voice.py
  risk.py
  privacy.py
  crypto/
    jwt_tokens.py
    audit_chain.py
    embedding_store.py
  protocols/
    repositories.py
    providers.py
```

---

## What Must Stay In the Host App

The host app should own all business-specific database logic.

### Business tables

- `patients`
- `doctors`
- `appointments`
- `auth_sessions`
- `auth_events`
- `voiceprints`

### Business services

- scheduling service
- doctor lookup
- availability queries
- booking logic
- app-specific auth orchestration
- Gemini/Vapi tool registry
- REST/WebSocket endpoints

### Why

These things are product-specific. If they move into `voiceguard`, the package stops being reusable and becomes tightly coupled to one schema and one industry use case.

---

## Key Design Principle

`voiceguard` should depend on abstractions, not your SQLite tables directly.

That means:

- `voiceguard` defines repository interfaces or protocols
- the host app implements them using SQLite

---

## Repository / Provider Interfaces

The package should define abstract interfaces such as:

```python
class PatientRepository(Protocol):
    def get_by_pesel(self, pesel: str) -> PatientRecord | None: ...

class AuthSessionRepository(Protocol):
    def create_session(self, ...): ...
    def update_session(self, ...): ...
    def get_session(self, session_id: str): ...

class VoiceprintRepository(Protocol):
    def get_voiceprint(self, patient_pesel: str): ...
    def save_voiceprint(self, patient_pesel: str, embedding: list[float], ...): ...

class AuditRepository(Protocol):
    def append_event(self, event: dict): ...

class OtpProvider(Protocol):
    def send_code(self, phone_number: str, code: str) -> None: ...
```

The package uses these interfaces. The host app supplies concrete implementations.

---

## Example Integration Shape

### In `voiceguard`

```python
session = VerificationSession(
    patient_repo=patient_repo,
    auth_repo=auth_repo,
    voiceprint_repo=voiceprint_repo,
    audit_repo=audit_repo,
    otp_provider=otp_provider,
)
```

### In the host app

```python
from voiceguard.session import VerificationSession
from myapp.repositories import (
    SqlitePatientRepository,
    SqliteAuthSessionRepository,
    SqliteVoiceprintRepository,
    SqliteAuditRepository,
)
from myapp.sms import TwilioOtpProvider

session = VerificationSession(
    patient_repo=SqlitePatientRepository(db),
    auth_repo=SqliteAuthSessionRepository(db),
    voiceprint_repo=SqliteVoiceprintRepository(db),
    audit_repo=SqliteAuditRepository(db),
    otp_provider=TwilioOtpProvider(),
)
```

This keeps the dependency reusable and lets each app provide its own DB adapter.

---

## Recommended Host App Structure

```text
myapp/
  database/
    schema.sql
    client.py
    migrations.py
  repositories/
    sqlite_patient_repository.py
    sqlite_auth_session_repository.py
    sqlite_voiceprint_repository.py
    sqlite_audit_repository.py
    sqlite_doctor_repository.py
    sqlite_appointment_repository.py
  services/
    auth_service.py
    scheduling_service.py
  agent/
    tool_registry.py
    live_agent.py
  server/
    api.py
    ws.py
```

### Boundaries

- `voiceguard` handles verification mechanics
- host app handles business behavior

---

## Tool Layer Design

The live agent should not call `voiceguard` directly for everything.

Instead:

1. agent calls host-app tools
2. host-app tools use:
   - `voiceguard` for auth/verification
   - host scheduling services for appointments

### Example tool responsibilities

- `verify_patient_identity`
  - host tool
  - uses host patient repository
  - may call `voiceguard` validation helpers

- `send_sms`
  - host tool
  - uses `voiceguard` OTP logic
  - persists session state in host DB

- `verify_voice`
  - host tool
  - uses `voiceguard` voice verification
  - updates host DB

- `find_doctor_availability`
  - host tool only
  - entirely app/business specific

- `book_appointment`
  - host tool only
  - entirely app/business specific

---

## What Not To Do

### Do not hardcode hospital scheduling into `voiceguard`

Bad:

- `voiceguard` imports `appointments`
- `voiceguard` knows about doctors and specialties
- `voiceguard` books visits directly

That makes the package non-reusable.

### Do not make `voiceguard` own the app database schema

Bad:

- package migrations tied to one product schema
- package assumes one SQLite file layout
- package creates unrelated business tables

### Do not let the model bypass the host app

The live model should call host tools, not manipulate package internals directly.

---

## Database Strategy

If another project imports `voiceguard`, there are 2 valid patterns:

### Option A: Shared DB, host-owned schema

Best for your current case.

- host app owns all tables
- `voiceguard` reads/writes through host repository adapters
- one SQLite database file

### Option B: Separate package-managed auth tables

Possible, but more complex.

- host app keeps business tables
- `voiceguard` keeps its own auth tables
- integration joins data across boundaries

This is usually worse for a small product because session coordination becomes harder.

### Recommendation

Use Option A.

One database, host-owned schema, package-level abstractions.

---

## Packaging Plan

### Phase 1

Extract only reusable code:

- session flow
- OTP logic
- voice logic
- JWT logic
- risk logic
- interfaces

### Phase 2

Create host adapters:

- SQLite repository implementations
- Twilio provider implementation
- event/audit adapters

### Phase 3

Refactor host tools:

- use `voiceguard` through adapters
- keep scheduling tools in host app

### Phase 4

Publish/use dependency:

- local editable install first
- then internal package or PyPI if needed

---

## Suggested API Shape For `voiceguard`

Keep the public API small:

```python
from voiceguard.session import VerificationSession
from voiceguard.models import VerificationResult
```

### Example

```python
session = VerificationSession(
    patient_repo=patient_repo,
    auth_repo=auth_repo,
    voiceprint_repo=voiceprint_repo,
    audit_repo=audit_repo,
    otp_provider=otp_provider,
    settings=settings,
)

session.start(pesel="02211312345")
session.send_otp()
session.verify_otp("123456")
result = session.verify_voice(audio_bytes)
```

Then the host app decides:

```python
if result.verified:
    scheduling_service.book_appointment(...)
```

---

## Final Recommendation

If you want `voiceguard` to be a dependency used by another project:

- make `voiceguard` reusable and schema-agnostic
- keep scheduling and database ownership in the host app
- connect them using repository and provider interfaces

That gives you:

- reusable security/auth logic
- a real database-backed application
- clean separation between product logic and dependency logic

