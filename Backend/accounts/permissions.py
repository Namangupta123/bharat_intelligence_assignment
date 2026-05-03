from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsManagerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'MANAGER'
        )


class IsUserRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'USER'
        )


class IsUserOrManagerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('USER', 'MANAGER')
        )
