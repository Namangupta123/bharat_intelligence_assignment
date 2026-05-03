from django.urls import path
from .views import ProfileEmailUpdateView, ProfilePasswordUpdateView, InviteUserView

urlpatterns = [
    path('profile/email/', ProfileEmailUpdateView.as_view(), name='profile-email-update'),
    path('profile/password/', ProfilePasswordUpdateView.as_view(), name='profile-password-update'),
    path('admin/invite/', InviteUserView.as_view(), name='admin-invite-user'),
]
