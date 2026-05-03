from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class TaskCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user', password='pass123', role='USER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='ADMIN'
        )

    def test_user_can_create_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/tasks/', {'title': 'New Task', 'description': 'desc'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.status, 'PENDING')

    def test_user_can_create_task_with_assigned_manager(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Task with manager', 'assigned_manager': self.manager.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.assigned_manager, self.manager)

    def test_user_cannot_assign_non_manager_as_manager(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Bad Task', 'assigned_manager': self.admin.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assigned_manager', response.data)

    def test_manager_cannot_create_task(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/tasks/', {'title': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_create_task(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/tasks/', {'title': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_task(self):
        response = self.client.post('/api/tasks/', {'title': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskListMineTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user', password='pass123', role='USER'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='pass123', role='USER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.task1 = Task.objects.create(title='Task 1', created_by=self.user)
        self.task2 = Task.objects.create(title='Task 2', created_by=self.user)
        self.task3 = Task.objects.create(title='Task 3', created_by=self.user2)

    def test_user_sees_only_own_tasks(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/tasks/mine/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [t['title'] for t in response.data]
        self.assertIn('Task 1', titles)
        self.assertIn('Task 2', titles)
        self.assertNotIn('Task 3', titles)

    def test_user2_sees_only_own_tasks(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/tasks/mine/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 3')

    def test_manager_cannot_access_mine_endpoint(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/tasks/mine/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_mine_endpoint(self):
        response = self.client.get('/api/tasks/mine/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskManagerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user', password='pass123', role='USER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.manager2 = User.objects.create_user(
            username='manager2', password='pass123', role='MANAGER'
        )
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='ADMIN'
        )
        self.task1 = Task.objects.create(
            title='Task 1', created_by=self.user, assigned_manager=self.manager
        )
        self.task2 = Task.objects.create(
            title='Task 2', created_by=self.user, assigned_manager=self.manager
        )
        self.task3 = Task.objects.create(
            title='Task 3', created_by=self.user, assigned_manager=self.manager2
        )

    def test_manager_can_view_assigned_tasks(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/tasks/assigned/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_manager_sees_only_own_assigned_tasks(self):
        self.client.force_authenticate(user=self.manager2)
        response = self.client.get('/api/tasks/assigned/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 3')

    def test_user_cannot_access_assigned_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/tasks/assigned/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_approve_task(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'APPROVED')

    def test_manager_can_reject_task(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'REJECTED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'REJECTED')

    def test_manager_cannot_set_status_to_pending(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'PENDING'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_cannot_update_task_assigned_to_other_manager(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task3.id}/status/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_task_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_update_task_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('tasks.email_tasks.send_task_status_email.delay')
    def test_email_task_dispatched_on_approve(self, mock_delay):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_called_once_with(
            task_id=self.task1.id,
            task_title=self.task1.title,
            new_status='APPROVED',
            recipient_email=self.user.email,
            recipient_name=self.user.username,
        )

    @patch('tasks.email_tasks.send_task_status_email.delay')
    def test_email_task_dispatched_on_reject(self, mock_delay):
        self.client.force_authenticate(user=self.manager)
        response = self.client.patch(
            f'/api/tasks/{self.task1.id}/status/',
            {'status': 'REJECTED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_called_once_with(
            task_id=self.task1.id,
            task_title=self.task1.title,
            new_status='REJECTED',
            recipient_email=self.user.email,
            recipient_name=self.user.username,
        )


class AdminTaskTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='ADMIN'
        )
        self.user = User.objects.create_user(
            username='user', password='pass123', role='USER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.task1 = Task.objects.create(title='Task 1', created_by=self.user)
        self.task2 = Task.objects.create(
            title='Task 2', created_by=self.user, assigned_manager=self.manager
        )

    def test_admin_can_list_all_tasks(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_task_list_contains_expected_fields(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/tasks/')
        first = response.data[0]
        for field in ['id', 'title', 'status', 'created_by', 'assigned_manager']:
            self.assertIn(field, first)

    def test_user_cannot_access_admin_tasks(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/admin/tasks/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_cannot_access_admin_tasks(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/admin/tasks/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_overview_returns_correct_counts(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_users'], 3)
        self.assertEqual(response.data['total_tasks'], 2)
        self.assertEqual(response.data['tasks_by_status']['PENDING'], 2)
        self.assertEqual(response.data['tasks_by_status']['APPROVED'], 0)
        self.assertEqual(response.data['tasks_by_status']['REJECTED'], 0)
        self.assertEqual(response.data['users_by_role']['ADMIN'], 1)
        self.assertEqual(response.data['users_by_role']['MANAGER'], 1)
        self.assertEqual(response.data['users_by_role']['USER'], 1)

    def test_overview_structure_contains_all_keys(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/overview/')
        for key in ['total_users', 'total_tasks', 'tasks_by_status', 'users_by_role']:
            self.assertIn(key, response.data)

    def test_manager_cannot_access_admin_overview(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/admin/overview/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_admin_overview(self):
        response = self.client.get('/api/admin/overview/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
