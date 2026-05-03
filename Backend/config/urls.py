from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import UserListView
from tasks.views import AdminTaskListView, AdminOverviewView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tasks/', include('tasks.urls')),
    path('api/admin/users/', UserListView.as_view(), name='admin-user-list'),
    path('api/admin/tasks/', AdminTaskListView.as_view(), name='admin-task-list'),
    path('api/admin/overview/', AdminOverviewView.as_view(), name='admin-overview'),
]
