from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_has_role_field(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(hasattr(user, 'role'))

    def test_default_role_is_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertEqual(user.role, 'USER')

    def test_role_can_be_set_to_admin(self):
        user = User.objects.create_user(
            username='adminuser', password='testpass123', role='ADMIN'
        )
        self.assertEqual(user.role, 'ADMIN')

    def test_role_can_be_set_to_manager(self):
        user = User.objects.create_user(
            username='manageruser', password='testpass123', role='MANAGER'
        )
        self.assertEqual(user.role, 'MANAGER')

    def test_str_returns_username(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertEqual(str(user), 'testuser')

    def test_role_choices_are_limited(self):
        field = User._meta.get_field('role')
        valid_choice_values = [choice[0] for choice in field.choices]
        self.assertIn('ADMIN', valid_choice_values)
        self.assertIn('MANAGER', valid_choice_values)
        self.assertIn('USER', valid_choice_values)
        self.assertEqual(len(valid_choice_values), 3)
