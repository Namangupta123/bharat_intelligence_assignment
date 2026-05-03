from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminUserListTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='pass123', role='ADMIN'
        )
        self.manager = User.objects.create_user(
            username='manager', password='pass123', role='MANAGER'
        )
        self.user = User.objects.create_user(
            username='user', password='pass123', role='USER'
        )

    def test_admin_can_list_all_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_list_contains_expected_fields(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/admin/users/')
        first = response.data[0]
        for field in ['id', 'username', 'email', 'role', 'date_joined', 'is_active']:
            self.assertIn(field, first)

    def test_manager_cannot_list_users(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_users(self):
        response = self.client.get('/api/admin/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
