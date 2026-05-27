import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailTransport:
    """Encapsulates low-level SMTP transport.

    Defaults to `SMTP_SERVER`/`SMTP_PORT` from environment variables so a
    local Mailpit (SMTP on 1025, web UI on 8025) can be used in development.
    """

    def __init__(self, server: Optional[str] = None, port: Optional[int] = None):
        """Create a transport bound to `server:port`.

        If no values are provided the environment is consulted.
        """
        self.server = server or os.getenv("SMTP_SERVER", "localhost")
        self.port = int(port or os.getenv("SMTP_PORT", 1025))

    def send(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send a single HTML email.

        Returns True on success, False on failure.
        """
        msg = MIMEMultipart()
        msg['From'] = "noreply@votreapp.com"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.send_message(msg)
            return True
        except Exception as exc:
            logger.exception("Failed to send email to %s", to_email)
            return False
