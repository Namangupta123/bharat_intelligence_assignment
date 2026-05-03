import logging
import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_task_status_email(self, task_id, task_title, new_status, recipient_email, recipient_name):
    if not recipient_email:
        logger.warning("Task %s has no recipient email, skipping notification.", task_id)
        return None

    status_verb = 'approved' if new_status == 'APPROVED' else 'rejected'
    payload = {
        "sender": {"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
        "to": [{"email": recipient_email, "name": recipient_name or recipient_email}],
        "subject": f"Your task has been {status_verb}",
        "htmlContent": (
            f"<html><body><h2>Task Status Update</h2>"
            f"<p>Hello {recipient_name or 'there'},</p>"
            f"<p>Your task <strong>{task_title}</strong> (ID: {task_id}) has been <strong>{new_status}</strong>.</p>"
            f"<p>Thank you,<br>{settings.BREVO_SENDER_NAME}</p></body></html>"
        ),
    }
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return {"status": "sent", "message_id": response.json().get("messageId")}
    except requests.RequestException as exc:
        logger.error("Failed to send email for task %s: %s", task_id, exc)
        raise self.retry(exc=exc)
