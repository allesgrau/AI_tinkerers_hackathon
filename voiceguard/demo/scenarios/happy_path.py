"""Happy path: normal verification, all steps pass."""

scenario = [
    # Agent greeting
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Dzień dobry, tu VoiceGuard. Proszę podać numer PESEL w celu weryfikacji tożsamości."},

    # User provides PESEL
    {"delay": 2.0, "type": "transcript.add", "speaker": "user", "text": "Tak, mój PESEL to 02211312345."},

    # PESEL verification
    {"delay": 0.3, "type": "step.update", "step": "pesel", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "PESEL 0221****345 → DB lookup...", "level": "info"},
    {"delay": 0.8, "type": "reasoning.add", "text": "Match: Jan Kowalski → phone: +48 600***23", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "pesel", "status": "verified", "patient_name": "Jan Kowalski"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"pesel_status": "verified"}},

    # Agent asks for SMS
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Dziękuję, Jan. Wysyłam teraz kod SMS na Twój numer telefonu. Proszę go odczytać."},

    # OTP sent
    {"delay": 0.3, "type": "step.update", "step": "otp", "status": "sending"},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP generated: 6 digits, SHA-256 hashed before storage", "level": "info"},
    {"delay": 1.0, "type": "reasoning.add", "text": "SMS sent via Twilio → delivery confirmed (SID: SM7f2a...)", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "otp", "status": "sent"},

    # User reads code
    {"delay": 3.0, "type": "transcript.add", "speaker": "user", "text": "Kod to 847291."},

    # OTP verification
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "OTP hash match ✓", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "otp", "status": "verified"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "verified", "otp_timing": "normal (4.2s)"}},

    # Voice verification starts in background
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Świetnie, kod poprawny. Proszę jeszcze chwilę poczekać na finalizację weryfikacji..."},
    {"delay": 0.3, "type": "step.update", "step": "voice", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "Voice buffer: 6.8s captured, SNR: 22dB (excellent)", "level": "info"},
    {"delay": 1.5, "type": "reasoning.add", "text": "Computing speaker embedding (ECAPA-TDNN, 192-dim)...", "level": "info"},
    {"delay": 1.0, "type": "reasoning.add", "text": "Embedding computed: L2-norm: 1.0, processing time: 340ms", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "Cosine similarity: 0.847 (threshold: 0.72) ✓", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "voice", "status": "verified", "score": 0.847},
    {"delay": 0.1, "type": "risk.update", "indicators": {"voice_status": "verified", "voice_score": 0.847, "voice_confidence": "green"}},

    # Session complete
    {"delay": 0.5, "type": "reasoning.add", "text": "ALL STEPS VERIFIED — issuing JWT token (exp: 300s)", "level": "info"},
    {"delay": 0.3, "type": "session.complete", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiZGVtby1oYXBweS1wYXRoIiwicGVzZWxfdmVyaWZpZWQiOnRydWUsIm90cF92ZXJpZmllZCI6dHJ1ZSwidm9pY2Vfc2NvcmUiOjAuODQ3fQ.demo", "rejected": False, "reason": ""},

    # Agent confirms
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Tożsamość zweryfikowana pomyślnie. Jak mogę Panu pomóc?"},
]
