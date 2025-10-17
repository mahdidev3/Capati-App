import unittest
from unittest.mock import patch, MagicMock
from email_sender import EmailService

class TestEmailService(unittest.TestCase):
    def setUp(self):
        """Set up the EmailService instance before each test."""
        self.email_service = EmailService(
            smtp_server="localhost",
            smtp_port=1025,
            default_from="system@localhost",
            admin_email="admin@localhost"
        )

    @patch('smtplib.SMTP')
    def test_send_warning_to_admin(self, mock_smtp):
        """Test sending a warning email to the admin."""
        # Arrange
        warning_message = "System running at 80% capacity."
        mock_server_instance = MagicMock()
        mock_smtp.return_value = mock_server_instance

        # Act
        self.email_service.send_warning_to_admin(warning_message)

        # Assert
        mock_smtp.assert_called_once_with("localhost", 1025, timeout=10)
        mock_server_instance.send_message.assert_called_once()
        mock_server_instance.quit.assert_called_once()

        # Inspect the email content
        sent_message = mock_server_instance.send_message.call_args[0][0]
        self.assertEqual(sent_message['From'], "system@localhost")
        self.assertEqual(sent_message['To'], "admin@localhost")
        self.assertEqual(sent_message['Subject'], "WARNING: System Alert")
        self.assertIn(warning_message, sent_message.get_payload()[0].get_payload())

    @patch('smtplib.SMTP')
    def test_send_error_to_admin(self, mock_smtp):
        """Test sending an error email to the admin."""
        # Arrange
        error_message = "Database connection failed."
        mock_server_instance = MagicMock()
        mock_smtp.return_value = mock_server_instance

        # Act
        self.email_service.send_error_to_admin(error_message)

        # Assert
        mock_smtp.assert_called_once_with("localhost", 1025, timeout=10)
        mock_server_instance.send_message.assert_called_once()
        mock_server_instance.quit.assert_called_once()

        # Inspect the email content
        sent_message = mock_server_instance.send_message.call_args[0][0]
        self.assertEqual(sent_message['From'], "system@localhost")
        self.assertEqual(sent_message['To'], "admin@localhost")
        self.assertEqual(sent_message['Subject'], "ERROR: Critical System Issue")
        self.assertIn(error_message, sent_message.get_payload()[0].get_payload())

    @patch('smtplib.SMTP')
    def test_smtp_failure(self, mock_smtp):
        """Test handling of SMTP connection failure."""
        # Arrange
        mock_smtp.side_effect = Exception("SMTP connection failed")
        warning_message = "System running at 80% capacity."

        # Act
        result = self.email_service.send_warning_to_admin(warning_message)

        # Assert
        self.assertFalse(result)  # Verify that the method returns False on failure
        mock_smtp.assert_called_once_with("localhost", 1025, timeout=10)

if __name__ == '__main__':
    unittest.main()