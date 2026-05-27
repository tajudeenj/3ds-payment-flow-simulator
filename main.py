"""
3-D Secure Payment Flow Simulator
===================================
Simulates the 3DS authentication flow for card-based transactions
Author: Tajudeen Jalaudin
Inspired by 3-D Secure implementation for UAE, UK & Iraq at ADIB
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
from datetime import datetime

app = FastAPI(title="3-D Secure Payment Flow Simulator", version="1.0.0")

# --- Mock Card Database ---
ENROLLED_CARDS = {
    "4111111111111111": {"otp": "123456", "enrolled": True, "country": "UAE"},
    "4222222222222222": {"otp": "654321", "enrolled": True, "country": "UK"},
    "4333333333333333": {"otp": "111222", "enrolled": True, "country": "Iraq"},
    "4000000000000000": {"otp": None, "enrolled": False, "country": "UAE"},
}

# In-memory session store
AUTH_SESSIONS = {}

# --- Models ---
class PaymentInitRequest(BaseModel):
    card_number: str
    amount: float
    currency: str = "AED"
    merchant_id: str
    merchant_name: str

class OTPVerifyRequest(BaseModel):
    session_id: str
    otp: str

class PaymentResult(BaseModel):
    session_id: str
    status: str
    eci: str          # Electronic Commerce Indicator
    cavv: Optional[str] = None
    message: str

# --- 3DS Flow ---
@app.post("/api/v1/3ds/initiate")
def initiate_3ds(request: PaymentInitRequest):
    """Step 1: Initiate 3DS authentication."""
    card = ENROLLED_CARDS.get(request.card_number)

    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "card_number": request.card_number[-4:],  # Mask card
        "amount": request.amount,
        "currency": request.currency,
        "merchant_id": request.merchant_id,
        "merchant_name": request.merchant_name,
        "timestamp": datetime.utcnow().isoformat(),
        "attempts": 0,
    }

    if not card or not card["enrolled"]:
        session["status"] = "NOT_ENROLLED"
        AUTH_SESSIONS[session_id] = session
        return {
            "session_id": session_id,
            "enrolled": False,
            "eci": "07",
            "message": "Card not enrolled in 3DS. Proceed with liability shift to merchant."
        }

    session["status"] = "PENDING_OTP"
    session["expected_otp"] = card["otp"]
    session["country"] = card["country"]
    AUTH_SESSIONS[session_id] = session

    return {
        "session_id": session_id,
        "enrolled": True,
        "status": "OTP_SENT",
        "masked_card": f"****{request.card_number[-4:]}",
        "message": f"OTP sent to registered mobile for card issued in {card['country']}."
    }

@app.post("/api/v1/3ds/verify", response_model=PaymentResult)
def verify_otp(request: OTPVerifyRequest):
    """Step 2: Verify OTP and complete 3DS authentication."""
    session = AUTH_SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    session["attempts"] += 1

    if session["attempts"] > 3:
        return PaymentResult(
            session_id=request.session_id,
            status="LOCKED",
            eci="07",
            message="Too many failed attempts. Card temporarily locked."
        )

    if request.otp != session.get("expected_otp"):
        remaining = 3 - session["attempts"]
        return PaymentResult(
            session_id=request.session_id,
            status="FAILED",
            eci="07",
            message=f"Incorrect OTP. {remaining} attempt(s) remaining."
        )

    # Success — generate CAVV
    cavv = hashlib.sha256(f"{request.session_id}{request.otp}".encode()).hexdigest()[:20].upper()
    session["status"] = "AUTHENTICATED"

    return PaymentResult(
        session_id=request.session_id,
        status="AUTHENTICATED",
        eci="05",   # Full 3DS authentication
        cavv=cavv,
        message="3DS Authentication successful. Payment authorized."
    )

@app.get("/api/v1/3ds/session/{session_id}")
def get_session(session_id: str):
    session = AUTH_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    safe = {k: v for k, v in session.items() if k != "expected_otp"}
    return safe

@app.get("/health")
def health():
    return {"status": "ok", "active_sessions": len(AUTH_SESSIONS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
