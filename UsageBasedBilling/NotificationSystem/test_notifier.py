import unittest
from unittest.mock import patch, MagicMock
from notifier import NotificationProcessor

class TestNotificationProcessor(unittest.TestCase):

    @patch('notifier.Consumer')
    def setUp(self, mock_consumer):
        self.processor = NotificationProcessor()

    @patch('notifier.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        mock_server = mock_smtp.return_value.__enter__.return_value
        
        result = self.processor.send_email('test@example.com', 'Subject', 'Body')
        
        self.assertTrue(result)
        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()

    @patch.object(NotificationProcessor, 'send_email')
    def test_process_notification(self, mock_send_email):
        data = {
            "email": "user@test.com",
            "subject": "Alert",
            "body": "Your usage is high"
        }
        self.processor.process_notification(data)
        mock_send_email.assert_called_once_with("user@test.com", "Alert", "Your usage is high")

if __name__ == '__main__':
    unittest.main()
