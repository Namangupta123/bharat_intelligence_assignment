from django.test import TestCase
from unittest.mock import MagicMock
from accounts.permissions import IsAdminRole, IsManagerRole, IsUserRole


def _mock_request(role=None, authenticated=True):
    request = MagicMock()
    if authenticated:
        user = MagicMock()
        user.is_authenticated = True
        user.role = role
        request.user = user
    else:
        request.user = MagicMock(is_authenticated=False)
    return request


class IsAdminRoleTest(TestCase):
    def test_admin_user_has_permission(self):
        perm = IsAdminRole()
        self.assertTrue(perm.has_permission(_mock_request('ADMIN'), None))

    def test_manager_user_denied(self):
        perm = IsAdminRole()
        self.assertFalse(perm.has_permission(_mock_request('MANAGER'), None))

    def test_user_role_denied(self):
        perm = IsAdminRole()
        self.assertFalse(perm.has_permission(_mock_request('USER'), None))

    def test_unauthenticated_denied(self):
        perm = IsAdminRole()
        self.assertFalse(perm.has_permission(_mock_request(authenticated=False), None))


class IsManagerRoleTest(TestCase):
    def test_manager_user_has_permission(self):
        perm = IsManagerRole()
        self.assertTrue(perm.has_permission(_mock_request('MANAGER'), None))

    def test_admin_denied(self):
        perm = IsManagerRole()
        self.assertFalse(perm.has_permission(_mock_request('ADMIN'), None))

    def test_user_role_denied(self):
        perm = IsManagerRole()
        self.assertFalse(perm.has_permission(_mock_request('USER'), None))

    def test_unauthenticated_denied(self):
        perm = IsManagerRole()
        self.assertFalse(perm.has_permission(_mock_request(authenticated=False), None))


class IsUserRoleTest(TestCase):
    def test_user_role_has_permission(self):
        perm = IsUserRole()
        self.assertTrue(perm.has_permission(_mock_request('USER'), None))

    def test_admin_denied(self):
        perm = IsUserRole()
        self.assertFalse(perm.has_permission(_mock_request('ADMIN'), None))

    def test_manager_denied(self):
        perm = IsUserRole()
        self.assertFalse(perm.has_permission(_mock_request('MANAGER'), None))

    def test_unauthenticated_denied(self):
        perm = IsUserRole()
        self.assertFalse(perm.has_permission(_mock_request(authenticated=False), None))
