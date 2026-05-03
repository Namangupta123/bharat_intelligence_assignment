from django.test import TestCase
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator', password='testpass123', role='USER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='testpass123', role='MANAGER'
        )

    def test_task_can_be_created_with_required_fields(self):
        task = Task.objects.create(
            title='Fix login bug',
            description='Login page returns 500 on mobile',
            created_by=self.user,
            assigned_manager=self.manager,
        )
        self.assertEqual(task.title, 'Fix login bug')
        self.assertEqual(task.description, 'Login page returns 500 on mobile')
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.assigned_manager, self.manager)

    def test_default_status_is_pending(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        self.assertEqual(task.status, 'PENDING')

    def test_status_can_be_set_to_approved(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        task.status = 'APPROVED'
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.status, 'APPROVED')

    def test_status_can_be_set_to_rejected(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        task.status = 'REJECTED'
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.status, 'REJECTED')

    def test_assigned_manager_is_optional(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        self.assertIsNone(task.assigned_manager)

    def test_str_returns_title(self):
        task = Task.objects.create(title='Fix login bug', created_by=self.user)
        self.assertEqual(str(task), 'Fix login bug')

    def test_task_has_timestamps(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    def test_deleting_user_deletes_their_created_tasks(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        self.user.delete()
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_deleting_manager_nullifies_assigned_manager(self):
        task = Task.objects.create(
            title='Test Task', created_by=self.user, assigned_manager=self.manager
        )
        self.manager.delete()
        task.refresh_from_db()
        self.assertIsNone(task.assigned_manager)

    def test_status_choices_are_limited(self):
        field = Task._meta.get_field('status')
        valid_choice_values = [choice[0] for choice in field.choices]
        self.assertIn('PENDING', valid_choice_values)
        self.assertIn('APPROVED', valid_choice_values)
        self.assertIn('REJECTED', valid_choice_values)
        self.assertEqual(len(valid_choice_values), 3)
