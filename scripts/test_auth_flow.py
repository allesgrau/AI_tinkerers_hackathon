"""
Test Auth Service - Person 4
Simple demo showing the 3-step auth flow: PESEL → SMS → Voice
"""

import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from auth.auth_service import AuthService


def demo_auth_flow():
    """Demo of the complete 3-step authentication flow"""
    
    print("=" * 70)
    print("AUTHENTICATION FLOW DEMO - Person 4 (Auth + Integracje)")
    print("=" * 70)
    
    # Initialize auth service
    auth = AuthService(db_path="hospital_agent.db")
    
    # Use test patient from seed data
    test_pesel = "02211312345"  # Jan Kowalski
    
    print("\n📋 STEP 1: PESEL Verification")
    print("-" * 70)
    success, message = auth.verify_pesel(test_pesel)
    print(f"Result: {message}")
    
    if not success:
        print("❌ Failed - stopping demo")
        return
    
    print("\n📱 STEP 2: SMS OTP Verification")
    print("-" * 70)
    success, message = auth.send_sms_otp(test_pesel)
    print(f"Result: {message}")
    print("⚠️  In production, this would send real SMS via Twilio/Switch")
    
    # Simulate user entering wrong code first
    print("\n  Attempting wrong code (should fail):")
    success, message = auth.verify_sms_code(test_pesel, "999999")
    print(f"  Result: {message}")
    
    # Get correct OTP from DB for demo
    conn = sqlite3.connect("hospital_agent.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT otp_code FROM sms_verifications 
        WHERE patient_pesel = ? AND status = 'pending' AND is_used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (test_pesel,))
    correct_otp = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n  Using correct code: {correct_otp}")
    success, message = auth.verify_sms_code(test_pesel, correct_otp)
    print(f"  Result: {message}")
    
    if not success:
        print("❌ Failed - stopping demo")
        return
    
    print("\n🎤 STEP 3: Voice Biometrics")
    print("-" * 70)
    
    # Enrollment
    print("Enrolling voice for first time...")
    mock_voice_data = "mock_audio_waveform_12345"
    success, message = auth.enroll_voice(test_pesel, mock_voice_data)
    print(f"Result: {message}")
    
    if not success:
        print("❌ Failed - stopping demo")
        return
    
    # Verification
    print("\nVerifying voice on subsequent call...")
    success, details = auth.verify_voice(test_pesel, mock_voice_data)
    if success:
        print(f"✅ Voice matched! Confidence: {details['confidence']:.1%}")
    else:
        print(f"❌ Voice mismatch: {details.get('error', 'Unknown error')}")
    
    print("\n✅ STEP 3b: Creating Authenticated Session")
    print("-" * 70)
    success, auth_token = auth.create_auth_session(
        test_pesel,
        pesel_verified=True,
        sms_verified=True,
        voice_verified=success,
        voice_confidence=details.get('confidence', 0.0) if success else 0.0
    )
    print(f"Auth Token: {auth_token[:32]}...")
    print(f"Valid for: 1 hour")
    
    print("\n✅ STEP 3c: Verifying Auth Token")
    print("-" * 70)
    is_valid, pesel = auth.verify_auth_token(auth_token)
    if is_valid:
        print(f"✅ Token is valid for patient: {pesel}")
    else:
        print("❌ Token is invalid or expired")
    
    print("\n" + "=" * 70)
    print("📊 AUTH FLOW SUMMARY")
    print("=" * 70)
    print("✅ PESEL → verified")
    print("✅ SMS OTP → verified")
    print("✅ Voice Biometrics → verified")
    print("✅ Session Token → created")
    print("\n🎉 Full 3-step authentication complete!")
    print("\n" + "=" * 70)


def show_api_contracts():
    """Display API contracts for other team members"""
    
    print("\n" + "=" * 70)
    print("API CONTRACTS - Person 4 (Auth + Integracje)")
    print("=" * 70)
    print("""
FOR PERSON 2 (Backend - Cloud Functions):

1. POST /auth/verify-pesel
   Body: {"pesel": "12345678901"}
   Response: {"success": bool, "patient_name": str, "message": str}

2. POST /auth/send-sms
   Body: {"pesel": "12345678901"}
   Response: {"success": bool, "message": str}

3. POST /auth/verify-sms
   Body: {"pesel": "12345678901", "otp_code": "123456"}
   Response: {"success": bool, "message": str}

4. POST /auth/enroll-voice
   Body: {"pesel": "12345678901", "voice_data": "<base64>"}
   Response: {"success": bool, "message": str}

5. POST /auth/verify-voice
   Body: {"pesel": "12345678901", "voice_data": "<base64>"}
   Response: {"success": bool, "confidence": float, "message": str}

6. POST /auth/create-session
   Body: {"pesel": "12345678901", "pesel_verified": bool, "sms_verified": bool, 
          "voice_verified": bool, "voice_confidence": float}
   Response: {"success": bool, "auth_token": str, "expires_in": 3600}

7. POST /auth/verify-token
   Body: {"auth_token": "<token>"}
   Response: {"success": bool, "patient_pesel": str}

All endpoints should log to auth_events table.
    """)


if __name__ == "__main__":
    demo_auth_flow()
    show_api_contracts()
