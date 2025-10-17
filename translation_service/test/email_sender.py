import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_server="localhost", smtp_port=1025, default_from="system@localhost", admin_email="admin@localhost"):
        """Initialize EmailService with SMTP settings, default sender, and admin email."""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.default_from = default_from
        self.admin_email = admin_email

    def _send_message(self, msg):
        """Helper method to handle SMTP connection and message sending."""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def send_warning_to_admin(self, warning_message):
        """Send a warning notification to the admin with a formatted subject and body."""
        subject = "WARNING: System Alert"
        body = f"Warning Alert\n\nDetails: {warning_message}\n\nPlease review the system status."
        msg = MIMEMultipart()
        msg['From'] = self.default_from
        msg['To'] = self.admin_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if self._send_message(msg):
            print(f"Warning email sent successfully to {self.admin_email}")

    def send_error_to_admin(self, error_message):
        """Send an error notification to the admin with a formatted subject and body."""
        subject = "ERROR: Critical System Issue"
        body = f"Critical Error\n\nDetails: {error_message}\n\nImmediate action required."
        msg = MIMEMultipart()
        msg['From'] = self.default_from
        msg['To'] = self.admin_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if self._send_message(msg):
            print(f"Error email sent successfully to {self.admin_email}")

# Example usage
if __name__ == "__main__":
    # Initialize the EmailService with local SMTP server and admin email
    email_service = EmailService(
        smtp_server="localhost",
        smtp_port=1025,
        default_from="system@localhost",
        admin_email="admin@localhost"
    )

    # Test warning email
    email_service.send_warning_to_admin(
        warning_message="System running at 80% capacity."
    )

    # Test error email
    email_service.send_error_to_admin(
        error_message="Database connection failed."
    )