# app/services/alerts.py
from app import mail
from flask_mail import Message
from config import Config

# Optional Twilio; guarded imports so devs without creds won’t crash
_twilio_client = None
def _twilio():
    global _twilio_client
    if _twilio_client is not None:
        return _twilio_client
    try:
        from twilio.rest import Client
        _twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    except Exception:
        _twilio_client = None
    return _twilio_client

def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    try:
        msg = Message(subject=subject,
                      sender=Config.MAIL_DEFAULT_SENDER,
                      recipients=[to_email])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[alerts] Email send failed: {e}")
        return False

def send_sms_alert(_to_number: str, _message: str) -> bool:
    # Implement later (Twilio SMS). For now, just log:
    print(f"[alerts] (stub) SMS to {_to_number}: {_message}")
    return True

def send_voice_call_alert(to_number: str, message: str) -> bool:
    """
    Places a phone call that ‘rings’ and speaks a message.
    Requires TWILIO_* config; gracefully no-ops if missing.
    """
    client = _twilio()
    if not client or not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, Config.TWILIO_FROM_NUMBER]):
        print("[alerts] Voice call skipped (Twilio not configured).")
        return False

    # TwiML to speak the message
    twiml = f'<Response><Say voice="alice">{message}</Say></Response>'
    try:
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=Config.TWILIO_FROM_NUMBER
        )
        print(f"[alerts] Voice call initiated: {call.sid}")
        return True
    except Exception as e:
        print(f"[alerts] Voice call failed: {e}")
        return False
