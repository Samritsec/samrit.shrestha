# app/services/notifier.py
from app.utils.entitlements import has_feature
from flask_mail import Message
from app import mail

def notify_event(event, admin_user):
    org_id = event.organization_id
    if has_feature(org_id, "alerts_email"):
        msg = Message(
            subject=f"[{event.severity.upper()}] {event.event_type}",
            recipients=[admin_user.email]
        )
        msg.body = f"{event.description}\n\nWhen: {event.timestamp}"
        mail.send(msg)
    # TODO: if has_feature(org_id, "alerts_sms"): send via Twilio
