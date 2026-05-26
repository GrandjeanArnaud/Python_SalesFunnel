import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from jinja2 import Environment, FileSystemLoader

from dotenv import load_dotenv

class EmailService:
    #pass

    load_dotenv() 

    #Configuration Jinja2
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    #_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    #Localhost 1025 pour les tests avec un serveur de test Mailpit
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

    @classmethod
    def send_template_email(cls, to_email: str, subject: str, html_content: str):
        """
        Méthode de classe pour rendre un template et envoyer un email.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = "noreply@votreapp.com"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Erreur d'envoi d'email: {e}")
            return False
