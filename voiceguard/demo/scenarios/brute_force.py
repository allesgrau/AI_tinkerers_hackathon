"""Brute force: attacker tries multiple OTP codes — rate limiting kicks in."""

scenario = [
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Dzień dobry, tu VoiceGuard. Proszę podać numer PESEL."},

    {"delay": 1.5, "type": "transcript.add", "speaker": "user", "text": "99123145678."},

    {"delay": 0.3, "type": "step.update", "step": "pesel", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "PESEL 9912****678 → DB lookup...", "level": "info"},
    {"delay": 0.8, "type": "reasoning.add", "text": "Match: Piotr Wiśniewski → phone: +48 789***56", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "pesel", "status": "verified", "patient_name": "Piotr Wiśniewski"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"pesel_status": "verified"}},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Wysyłam kod SMS."},
    {"delay": 0.3, "type": "step.update", "step": "otp", "status": "sending"},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP generated: 6 digits, SHA-256 hashed before storage", "level": "info"},
    {"delay": 1.0, "type": "step.update", "step": "otp", "status": "sent"},

    # Attempt 1 — wrong
    {"delay": 1.0, "type": "transcript.add", "speaker": "user", "text": "111111."},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.3, "type": "reasoning.add", "text": "OTP mismatch — attempt 1/3", "level": "warn"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "failed", "otp_attempts": 1}},

    # Attempt 2 — wrong, suspiciously fast
    {"delay": 0.8, "type": "transcript.add", "speaker": "user", "text": "222222."},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.3, "type": "reasoning.add", "text": "OTP mismatch — attempt 2/3", "level": "warn"},
    {"delay": 0.2, "type": "reasoning.add", "text": "WARNING: rapid retry detected (0.8s between attempts)", "level": "warn"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "failed", "otp_attempts": 2, "otp_timing": "suspicious (0.8s)"}},

    # Attempt 3 — wrong, lockout
    {"delay": 0.5, "type": "transcript.add", "speaker": "user", "text": "333333."},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.3, "type": "reasoning.add", "text": "OTP mismatch — attempt 3/3 — MAX ATTEMPTS REACHED", "level": "error"},
    {"delay": 0.2, "type": "reasoning.add", "text": "Session locked — brute force protection triggered", "level": "error"},
    {"delay": 0.2, "type": "reasoning.add", "text": "Event logged to audit chain: brute_force_lockout", "level": "error"},
    {"delay": 0.1, "type": "step.update", "step": "otp", "status": "failed"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "locked", "otp_attempts": 3, "otp_timing": "suspicious", "threat_level": "high"}},

    {"delay": 0.3, "type": "session.complete", "token": None, "rejected": True, "reason": "OTP brute force — session locked after 3 failed attempts"},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Przepraszam, przekroczono limit prób. Sesja została zablokowana ze względów bezpieczeństwa. Proszę skontaktować się z placówką osobiście."},
]
