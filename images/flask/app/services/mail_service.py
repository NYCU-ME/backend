import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailService:
    def __init__(self, logger, smtp_server, smtp_port, smtp_user, smtp_pass, smtp_from):
        self.logger = logger
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.smtp_from = smtp_from

    def send_mail(self, to, subject, body):
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_from
            message["To"] = to
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_from, to, message.as_string())
                self.logger.debug("Email sent successfully")
        except Exception as e:
            self.logger.warning("Error sending email: %s", str(e))
