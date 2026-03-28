"""
Auth Service - Person 4: Authentication + Integrations
Handles PESEL verification, SMS OTP, and voice biometrics
"""

import sqlite3
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import re

# ============ MOCK INTEGRATIONS ============
# In production, these would call real APIs (Twilio, Vertex AI, etc.)

class MockSMSProvider:
    """Mock SMS provider - logs OTP codes to console instead of sending"""
    
    @staticmethod
    def send_sms(phone_number: str, otp_code: str) -> bool:
        """Mock SMS send"""
        print(f"📱 [MOCK SMS] Sending OTP to {phone_number}: {otp_code}")
        return True


class MockVoiceBiometrics:
    """Mock voice biometrics - simulates Vertex AI or similar"""
    
    @staticmethod
    def enroll_voice(patient_pesel: str, voice_data: str) -> Dict:
        """Mock voice enrollment - creates a fake speaker_id"""
        speaker_id = f"speaker_{secrets.token_hex(8)}"
        voiceprint_hash = hashlib.sha256(voice_data.encode()).hexdigest()
        print(f"🎤 [MOCK VOICE] Enrolled voice for {patient_pesel} → {speaker_id}")
        return {
            "speaker_id": speaker_id,
            "voiceprint_hash": voiceprint_hash,
            "success": True
        }
    
    @staticmethod
    def verify_voice(patient_pesel: str, voice_data: str, stored_voiceprint: str) -> Dict:
        """Mock voice verification - returns random confidence (60-99%)"""
        confidence = secrets.randbelow(40) + 60  # 60-99%
        is_match = confidence > 85
        print(f"🎤 [MOCK VOICE] Verified voice for {patient_pesel} → {confidence}% confidence")
        return {
            "is_match": is_match,
            "confidence": confidence / 100.0,
            "success": True
        }


# ============ AUTH SERVICE ============

class AuthService:
    """Core authentication service"""
    
    def __init__(self, db_path: str = "hospital_agent.db"):
        self.db_path = db_path
        self.sms_provider = MockSMSProvider()
        self.voice_biometrics = MockVoiceBiometrics()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def log_auth_event(self, patient_pesel: Optional[str], event_type: str, 
                       status: str, details: str = "", ip_address: str = "127.0.0.1") -> None:
        """Log authentication event for audit trail"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auth_events (patient_pesel, event_type, status, details, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_pesel, event_type, status, details, ip_address))
        conn.commit()
        conn.close()
    
    # ============ STEP 1: PESEL VERIFICATION ============
    
    def verify_pesel(self, pesel: str) -> Tuple[bool, str]:
        """
        Step 1: Verify PESEL and get patient details
        Returns (is_valid, patient_name or error_message)
        """
        # Validate PESEL format
        if not self._is_valid_pesel_format(pesel):
            self.log_auth_event(None, "pesel_lookup", "failure", "Invalid PESEL format")
            return False, "Invalid PESEL format (must be 11 digits)"
        
        # Check if patient exists
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, phone_number FROM patients WHERE pesel = ?", (pesel,))
        patient = cursor.fetchone()
        conn.close()
        
        if not patient:
            self.log_auth_event(pesel, "pesel_lookup", "failure", "Patient not found")
            return False, "Patient not found in system"
        
        self.log_auth_event(pesel, "pesel_lookup", "success", f"Patient: {patient['full_name']}")
        return True, patient['full_name']
    
    @staticmethod
    def _is_valid_pesel_format(pesel: str) -> bool:
        """Validate PESEL format (11 digits)"""
        return isinstance(pesel, str) and len(pesel) == 11 and pesel.isdigit()
    
    # ============ STEP 2: SMS OTP VERIFICATION ============
    
    def send_sms_otp(self, pesel: str) -> Tuple[bool, str]:
        """
        Step 2: Send SMS with OTP code to patient's phone
        Returns (success, message)
        """
        # Get patient phone
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM patients WHERE pesel = ?", (pesel,))
        patient = cursor.fetchone()
        conn.close()
        
        if not patient:
            return False, "Patient not found"
        
        # Generate OTP
        otp_code = self._generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Store in DB
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sms_verifications (patient_pesel, otp_code, phone_number, expires_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (pesel, otp_code, patient['phone_number'], expires_at, "pending"))
        conn.commit()
        conn.close()
        
        # Send SMS (mock)
        self.sms_provider.send_sms(patient['phone_number'], otp_code)
        self.log_auth_event(pesel, "sms_sent", "success")
        
        return True, f"OTP sent to {patient['phone_number']}"
    
    def verify_sms_code(self, pesel: str, otp_code: str) -> Tuple[bool, str]:
        """
        Step 2b: Verify SMS OTP code
        Returns (success, message)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Find OTP
        cursor.execute("""
            SELECT verification_id, otp_code, expires_at, status, attempts
            FROM sms_verifications
            WHERE patient_pesel = ? AND is_used = 0 AND status = 'pending'
            ORDER BY created_at DESC LIMIT 1
        """, (pesel,))
        
        verification = cursor.fetchone()
        
        if not verification:
            self.log_auth_event(pesel, "sms_verified", "failure", "No pending OTP found")
            return False, "No pending OTP found"
        
        # Check if expired
        if datetime.fromisoformat(verification['expires_at']) < datetime.utcnow():
            cursor.execute("UPDATE sms_verifications SET status = ? WHERE verification_id = ?", 
                          ("expired", verification['verification_id']))
            conn.commit()
            self.log_auth_event(pesel, "sms_verified", "failure", "OTP expired")
            conn.close()
            return False, "OTP has expired"
        
        # Check attempts
        if verification['attempts'] >= 3:
            cursor.execute("UPDATE sms_verifications SET status = ? WHERE verification_id = ?", 
                          ("expired", verification['verification_id']))
            conn.commit()
            self.log_auth_event(pesel, "sms_verified", "failure", "Max attempts exceeded")
            conn.close()
            return False, "Too many attempts"
        
        # Verify code
        if verification['otp_code'] != otp_code:
            cursor.execute("UPDATE sms_verifications SET attempts = attempts + 1 WHERE verification_id = ?", 
                          (verification['verification_id'],))
            conn.commit()
            self.log_auth_event(pesel, "sms_verified", "failure", f"Wrong code (attempt {verification['attempts'] + 1}/3)")
            conn.close()
            return False, "Wrong OTP code"
        
        # Mark as used
        cursor.execute("UPDATE sms_verifications SET is_used = 1, status = ? WHERE verification_id = ?", 
                      ("verified", verification['verification_id']))
        conn.commit()
        conn.close()
        
        self.log_auth_event(pesel, "sms_verified", "success")
        return True, "SMS verified successfully"
    
    @staticmethod
    def _generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(999999)).zfill(6)
    
    # ============ STEP 3: VOICE BIOMETRICS ============
    
    def enroll_voice(self, pesel: str, voice_data: str) -> Tuple[bool, str]:
        """
        Step 3: Enroll voice for patient (first time registration)
        Returns (success, message)
        """
        # Call mock voice service
        result = self.voice_biometrics.enroll_voice(pesel, voice_data)
        
        if not result['success']:
            self.log_auth_event(pesel, "voice_enrolled", "failure", "Voice enrollment failed")
            return False, "Voice enrollment failed"
        
        # Store voiceprint in DB
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if already enrolled
        cursor.execute("SELECT voiceprint_id FROM voiceprints WHERE patient_pesel = ?", (pesel,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE voiceprints 
                SET voiceprint_hash = ?, speaker_id = ?, last_updated = CURRENT_TIMESTAMP
                WHERE patient_pesel = ?
            """, (result['voiceprint_hash'], result['speaker_id'], pesel))
        else:
            cursor.execute("""
                INSERT INTO voiceprints (patient_pesel, voiceprint_hash, speaker_id)
                VALUES (?, ?, ?)
            """, (pesel, result['voiceprint_hash'], result['speaker_id']))
        
        conn.commit()
        conn.close()
        
        self.log_auth_event(pesel, "voice_enrolled", "success", result['speaker_id'])
        return True, "Voice enrolled successfully"
    
    def verify_voice(self, pesel: str, voice_data: str) -> Tuple[bool, Dict]:
        """
        Step 3b: Verify voice for session authentication
        Returns (success, details_dict)
        """
        # Get stored voiceprint
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT voiceprint_hash FROM voiceprints WHERE patient_pesel = ?", (pesel,))
        voiceprint = cursor.fetchone()
        conn.close()
        
        if not voiceprint:
            self.log_auth_event(pesel, "voice_verified", "failure", "No voiceprint enrolled")
            return False, {"error": "Voice not enrolled for this patient"}
        
        # Call mock voice service
        result = self.voice_biometrics.verify_voice(pesel, voice_data, voiceprint['voiceprint_hash'])
        
        if not result['success']:
            self.log_auth_event(pesel, "voice_verified", "failure", "Voice verification failed")
            return False, {"error": "Voice verification failed"}
        
        event_status = "success" if result['is_match'] else "failure"
        self.log_auth_event(pesel, "voice_verified", event_status, 
                           f"Confidence: {result['confidence']:.2%}")
        
        return result['is_match'], {
            "is_match": result['is_match'],
            "confidence": result['confidence']
        }
    
    # ============ SESSION MANAGEMENT ============
    
    def create_auth_session(self, pesel: str, pesel_verified: bool = False, 
                           sms_verified: bool = False, voice_verified: bool = False,
                           voice_confidence: float = 0.0) -> Tuple[bool, str]:
        """
        Create authenticated session
        Returns (success, auth_token or error_message)
        """
        session_id = secrets.token_hex(16)
        auth_token = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auth_sessions 
            (session_id, patient_pesel, auth_token, pesel_verified, sms_verified, 
             voice_verified, voice_confidence, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, pesel, auth_token, 
              1 if pesel_verified else 0,
              1 if sms_verified else 0,
              1 if voice_verified else 0,
              voice_confidence, expires_at, "active"))
        conn.commit()
        conn.close()
        
        self.log_auth_event(pesel, "session_created", "success", f"Token: {auth_token[:16]}...")
        return True, auth_token
    
    def verify_auth_token(self, auth_token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify auth token and return patient_pesel if valid
        Returns (is_valid, patient_pesel or None)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_pesel, expires_at, status
            FROM auth_sessions
            WHERE auth_token = ?
        """, (auth_token,))
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return False, None
        
        if session['status'] != 'active':
            return False, None
        
        if datetime.fromisoformat(session['expires_at']) < datetime.utcnow():
            return False, None
        
        return True, session['patient_pesel']


# ============ API CONTRACTS (for other team members) ============

"""
API ENDPOINTS TO IMPLEMENT (for Person 2 - Backend):

1. POST /auth/verify-pesel
   Input: {"pesel": "12345678901"}
   Output: {"success": true, "patient_name": "Jan Kowalski", "message": "PESEL verified"}
           {"success": false, "error": "Patient not found"}

2. POST /auth/send-sms
   Input: {"pesel": "12345678901"}
   Output: {"success": true, "message": "OTP sent to +48501111222"}
           {"success": false, "error": "Patient not found"}

3. POST /auth/verify-sms
   Input: {"pesel": "12345678901", "otp_code": "123456"}
   Output: {"success": true, "message": "SMS verified"}
           {"success": false, "error": "Wrong OTP code"}

4. POST /auth/enroll-voice
   Input: {"pesel": "12345678901", "voice_data": "<base64_audio>"}
   Output: {"success": true, "message": "Voice enrolled"}
           {"success": false, "error": "Voice enrollment failed"}

5. POST /auth/verify-voice
   Input: {"pesel": "12345678901", "voice_data": "<base64_audio>"}
   Output: {"success": true, "confidence": 0.92, "message": "Voice verified"}
           {"success": false, "confidence": 0.45, "error": "Voice does not match"}

6. POST /auth/create-session
   Input: {"pesel": "12345678901", "pesel_verified": true, "sms_verified": true, "voice_verified": true, "voice_confidence": 0.92}
   Output: {"success": true, "auth_token": "<token>", "expires_in": 3600}
           {"success": false, "error": "Missing verification steps"}

7. POST /auth/verify-token
   Input: {"auth_token": "<token>"}
   Output: {"success": true, "patient_pesel": "12345678901"}
           {"success": false, "error": "Invalid or expired token"}
"""
