from django.urls import path
from .views import (
    TaskCreateView,
    TaskListMineView,
    TaskListAssignedView,
    TaskStatusUpdateView,
)

urlpatterns = [
    path('', TaskCreateView.as_view(), name='task-create'),
    path('mine/', TaskListMineView.as_view(), name='task-mine'),
    path('assigned/', TaskListAssignedView.as_view(), name='task-assigned'),
    path('<int:pk>/status/', TaskStatusUpdateView.as_view(), name='task-status'),
]
