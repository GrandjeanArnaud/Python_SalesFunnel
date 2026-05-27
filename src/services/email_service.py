from dotenv import load_dotenv
from src.services.email_transport import EmailTransport
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class EmailService:
    @classmethod
    def send_template_email(cls, to_email: str, subject: str, html_content: str) -> bool:
        """Send rendered HTML to `to_email` using configured transport.

        This higher-level service is intentionally minimal: rendering is done
        by the caller and this class delegates sending to `EmailTransport`.
        Returns True on success and False on failure.
        """
        transport = EmailTransport()
        ok = transport.send(to_email, subject, html_content)
        if not ok:
            logger.error("Failed to send email to %s", to_email)
        return ok
