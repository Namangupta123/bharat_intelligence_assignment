from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import UserListView, ManagerListView, CustomTokenObtainPairView
from tasks.views import AdminTaskListView, AdminOverviewView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tasks/', include('tasks.urls')),
    path('api/', include('accounts.urls')),
    path('api/managers/', ManagerListView.as_view(), name='manager-list'),
    path('api/admin/users/', UserListView.as_view(), name='admin-user-list'),
    path('api/admin/tasks/', AdminTaskListView.as_view(), name='admin-task-list'),
    path('api/admin/overview/', AdminOverviewView.as_view(), name='admin-overview'),
]
