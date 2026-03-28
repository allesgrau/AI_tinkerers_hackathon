"""Replay attack: attacker plays back a recording — anti-spoofing detects it (future feature preview)."""

scenario = [
    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Dzień dobry, tu VoiceGuard. Proszę podać numer PESEL."},

    {"delay": 2.0, "type": "transcript.add", "speaker": "user", "text": "02211312345."},

    {"delay": 0.3, "type": "step.update", "step": "pesel", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "PESEL 0221****345 → DB lookup...", "level": "info"},
    {"delay": 0.8, "type": "reasoning.add", "text": "Match: Jan Kowalski → phone: +48 600***23", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "pesel", "status": "verified", "patient_name": "Jan Kowalski"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"pesel_status": "verified"}},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Wysyłam kod SMS."},
    {"delay": 0.3, "type": "step.update", "step": "otp", "status": "sending"},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP generated: 6 digits, SHA-256 hashed before storage", "level": "info"},
    {"delay": 1.0, "type": "step.update", "step": "otp", "status": "sent"},

    {"delay": 3.0, "type": "transcript.add", "speaker": "user", "text": "Kod to 583920."},
    {"delay": 0.2, "type": "reasoning.add", "text": "OTP input: ****** → verifying hash...", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "OTP hash match ✓", "level": "info"},
    {"delay": 0.1, "type": "step.update", "step": "otp", "status": "verified"},
    {"delay": 0.1, "type": "risk.update", "indicators": {"otp_status": "verified"}},

    # Voice analysis — replay detected
    {"delay": 0.5, "type": "step.update", "step": "voice", "status": "in_progress"},
    {"delay": 0.2, "type": "reasoning.add", "text": "Voice buffer: 7.2s captured, SNR: 14dB (below average)", "level": "warn"},
    {"delay": 1.0, "type": "reasoning.add", "text": "Computing speaker embedding (ECAPA-TDNN, 192-dim)...", "level": "info"},
    {"delay": 0.8, "type": "reasoning.add", "text": "Embedding computed: L2-norm: 1.0", "level": "info"},
    {"delay": 0.5, "type": "reasoning.add", "text": "Cosine similarity: 0.891 (threshold: 0.72) — score looks valid", "level": "info"},

    # Anti-spoofing analysis
    {"delay": 0.3, "type": "reasoning.add", "text": "Running anti-spoofing analysis...", "level": "info"},
    {"delay": 1.0, "type": "reasoning.add", "text": "Spectral flatness: 0.23 (expected >0.4 for live speech)", "level": "warn"},
    {"delay": 0.5, "type": "reasoning.add", "text": "Compression artifacts detected: MP3 re-encoding signature found", "level": "error"},
    {"delay": 0.3, "type": "reasoning.add", "text": "Zero-crossing rate anomaly: consistent with loudspeaker playback", "level": "error"},
    {"delay": 0.2, "type": "reasoning.add", "text": "ANTI-SPOOF VERDICT: REPLAY ATTACK DETECTED (confidence: 94%)", "level": "error"},

    {"delay": 0.1, "type": "step.update", "step": "voice", "status": "failed", "score": 0.891},
    {"delay": 0.1, "type": "risk.update", "indicators": {
        "voice_status": "failed",
        "voice_score": 0.891,
        "voice_confidence": "red",
        "anti_spoof": "replay_detected",
        "threat_level": "critical",
    }},

    {"delay": 0.3, "type": "reasoning.add", "text": "Session rejected — replay attack. High similarity score but non-live audio source.", "level": "error"},
    {"delay": 0.2, "type": "session.complete", "token": None, "rejected": True, "reason": "Replay attack detected — recorded audio, not live speaker"},

    {"delay": 0.5, "type": "transcript.add", "speaker": "agent", "text": "Przepraszam, wykryliśmy nieprawidłowość w weryfikacji głosowej. Sesja została odrzucona. Proszę o kontakt osobisty z placówką."},
]
