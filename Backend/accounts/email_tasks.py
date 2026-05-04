import logging
import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, ignore_result=True)
def send_invitation_email(self, username, temp_password, recipient_email, role):
    if not recipient_email:
        logger.warning("Invitation has no recipient email, skipping.")
        return None

    role_display = role.capitalize()
    payload = {
        "sender": {"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
        "to": [{"email": recipient_email, "name": username}],
        "subject": f"Welcome to Task Manager — your {role_display} account",
        "htmlContent": (
            f"<html><body>"
            f"<h2>Welcome to Task Manager</h2>"
            f"<p>Hello {username},</p>"
            f"<p>An administrator has created a <strong>{role_display}</strong> account for you.</p>"
            f"<p><strong>Username:</strong> {username}<br>"
            f"<strong>Temporary password:</strong> {temp_password}</p>"
            f"<p>Please log in and change your password immediately from Profile Settings.</p>"
            f"<p>Thank you,<br>{settings.BREVO_SENDER_NAME}</p>"
            f"</body></html>"
        ),
    }
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": settings.BREVO_API_KEY.strip(), "Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return {"status": "sent", "message_id": response.json().get("messageId")}
    except requests.RequestException as exc:
        logger.error("Failed to send invitation email to %s: %s", recipient_email, exc)
        raise self.retry(exc=exc)
