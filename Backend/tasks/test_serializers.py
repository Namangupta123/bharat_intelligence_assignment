from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock
from tasks.serializers import TaskCreateSerializer, TaskStatusUpdateSerializer

User = get_user_model()


class TaskCreateSerializerTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='ADMIN'
        )
        self.user = User.objects.create_user(
            username='creator', password='pass123', role='USER'
        )

    def _make_request(self, user):
        request = MagicMock()
        request.user = user
        return request

    def test_valid_data_with_no_manager_passes(self):
        serializer = TaskCreateSerializer(
            data={'title': 'My Task'},
            context={'request': self._make_request(self.user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_valid_data_with_manager_passes(self):
        serializer = TaskCreateSerializer(
            data={'title': 'My Task', 'assigned_manager': self.manager.id},
            context={'request': self._make_request(self.user)},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_assigning_non_manager_raises_validation_error(self):
        serializer = TaskCreateSerializer(
            data={'title': 'My Task', 'assigned_manager': self.admin.id},
            context={'request': self._make_request(self.user)},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('assigned_manager', serializer.errors)

    def test_create_sets_created_by_from_request(self):
        serializer = TaskCreateSerializer(
            data={'title': 'My Task'},
            context={'request': self._make_request(self.user)},
        )
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.created_by, self.user)


class TaskStatusUpdateSerializerTest(TestCase):
    def test_approved_is_valid(self):
        serializer = TaskStatusUpdateSerializer(data={'status': 'APPROVED'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejected_is_valid(self):
        serializer = TaskStatusUpdateSerializer(data={'status': 'REJECTED'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_pending_is_invalid(self):
        serializer = TaskStatusUpdateSerializer(data={'status': 'PENDING'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_garbage_value_is_invalid(self):
        serializer = TaskStatusUpdateSerializer(data={'status': 'DONE'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
