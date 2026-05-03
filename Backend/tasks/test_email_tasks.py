from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()

BREVO_SETTINGS = {
    'BREVO_API_KEY': 'test-api-key',
    'BREVO_SENDER_EMAIL': 'sender@test.com',
    'BREVO_SENDER_NAME': 'Test Sender',
}


@override_settings(**BREVO_SETTINGS)
class SendTaskStatusEmailTest(TestCase):
    def setUp(self):
        from tasks.email_tasks import send_task_status_email
        self.task = send_task_status_email

    @patch('tasks.email_tasks.requests.post')
    def test_sends_email_on_approved(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'abc123'})
        result = self.task.apply(args=[1, 'Fix Bug', 'APPROVED', 'user@example.com', 'Alice']).get()
        self.assertEqual(result['status'], 'sent')
        self.assertEqual(result['message_id'], 'abc123')

    @patch('tasks.email_tasks.requests.post')
    def test_sends_email_on_rejected(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'xyz789'})
        result = self.task.apply(args=[2, 'Deploy App', 'REJECTED', 'user@example.com', 'Bob']).get()
        self.assertEqual(result['status'], 'sent')

    @patch('tasks.email_tasks.requests.post')
    def test_payload_uses_brevo_settings(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'id1'})
        self.task.apply(args=[3, 'My Task', 'APPROVED', 'user@example.com', 'Carol']).get()
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]['json']
        self.assertEqual(payload['sender']['email'], 'sender@test.com')
        self.assertEqual(payload['sender']['name'], 'Test Sender')
        self.assertEqual(payload['to'][0]['email'], 'user@example.com')
        self.assertEqual(payload['to'][0]['name'], 'Carol')

    @patch('tasks.email_tasks.requests.post')
    def test_subject_contains_approved(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'id2'})
        self.task.apply(args=[4, 'Task A', 'APPROVED', 'user@example.com', 'Dave']).get()
        payload = mock_post.call_args[1]['json']
        self.assertIn('approved', payload['subject'].lower())

    @patch('tasks.email_tasks.requests.post')
    def test_subject_contains_rejected(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'id3'})
        self.task.apply(args=[5, 'Task B', 'REJECTED', 'user@example.com', 'Eve']).get()
        payload = mock_post.call_args[1]['json']
        self.assertIn('rejected', payload['subject'].lower())

    @patch('tasks.email_tasks.requests.post')
    def test_html_content_includes_task_title(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {'messageId': 'id4'})
        self.task.apply(args=[6, 'Unique Task Title', 'APPROVED', 'user@example.com', 'Frank']).get()
        payload = mock_post.call_args[1]['json']
        self.assertIn('Unique Task Title', payload['htmlContent'])

    @patch('tasks.email_tasks.requests.post')
    def test_skips_email_when_no_recipient(self, mock_post):
        result = self.task.apply(args=[7, 'Task C', 'APPROVED', '', 'Ghost']).get()
        self.assertIsNone(result)
        mock_post.assert_not_called()

    @patch('tasks.email_tasks.requests.post')
    def test_skips_email_when_recipient_is_none(self, mock_post):
        result = self.task.apply(args=[8, 'Task D', 'REJECTED', None, None]).get()
        self.assertIsNone(result)
        mock_post.assert_not_called()

    @patch('tasks.email_tasks.requests.post')
    def test_retries_on_request_exception(self, mock_post):
        import requests as req_lib
        mock_post.side_effect = req_lib.RequestException('timeout')
        with self.assertRaises(Exception):
            self.task.apply(args=[9, 'Task E', 'APPROVED', 'user@example.com', 'Hana']).get()
