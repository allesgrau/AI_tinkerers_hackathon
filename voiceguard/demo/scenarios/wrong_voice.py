"""Wrong voice: PESEL and OTP pass, but voice doesn't match — impersonation attempt."""

scenario = [
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Dzień dobry, tu VoiceGuard. Proszę podać numer PESEL."},

    {"delay": 2.0, "type": "transcript.add", "speaker": "user", "text": "PESEL 83051298765."},

    {"delay": 0.3, "type": "step.update", "step": "pesel", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "PESEL 8305****765 → DB lookup...", "level": "info"},
    {"delay": 0.8, "type": "reasoning.add", "text": "Match: Anna Nowak → phone: +48 512***89", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "pesel", "status": "verified", "patient_name": "Anna Nowak"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"pesel_status": "verified"}},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Wysyłam kod SMS. Proszę go odczytać."},
    {"delay": 0.3, "type": "step.update", "step": "otp", "status": "sending"},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP generated: 6 digits, SHA-256 hashed before storage", "level": "info"},
    {"delay": 1.0, "type": "step.update", "step": "otp", "status": "sent"},

    {"delay": 3.5, "type": "transcript.add", "speaker": "user", "text": "Kod to 193847."},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "OTP hash match ✓", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "otp", "status": "verified"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "verified"}},

    # Voice mismatch!
    {"delay": 0.5, "type": "step.update", "step": "voice", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "Voice buffer: 5.1s captured, SNR: 19dB (good)", "level": "info"},
    {"delay": 1.5, "type": "reasoning.add", "text": "Computing speaker embedding (ECAPA-TDNN, 192-dim)...", "level": "info"},
    {"delay": 1.0, "type": "reasoning.add", "text": "Embedding computed: L2-norm: 1.0", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "Cosine similarity: 0.312 (threshold: 0.72) — MISMATCH", "level": "error"},
    {"delay": 0.2, "type": "reasoning.add", "text": "ALERT: Voice does not match enrolled profile for Anna Nowak", "level": "error"},
    {"delay": 0.1, "type": "step.update", "step": "voice", "status": "failed", "score": 0.312},
    {"delay": 0.1, "type": "risk.update", "indicators": {"voice_status": "failed", "voice_score": 0.312, "voice_confidence": "red"}},

    {"delay": 0.3, "type": "reasoning.add", "text": "Potential impersonation detected — session rejected, event logged to audit chain", "level": "error"},
    {"delay": 0.2, "type": "session.complete", "token": None, "rejected": True, "reason": "Voice mismatch — possible impersonation"},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Przepraszam, weryfikacja głosowa nie powiodła się. Nie mogę potwierdzić Pana tożsamości. Proszę skontaktować się z placówką osobiście."},
]
