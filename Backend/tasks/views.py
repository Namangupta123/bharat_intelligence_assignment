from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskStatusUpdateSerializer
from accounts.permissions import IsAdminRole, IsManagerRole, IsUserRole

User = get_user_model()


class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [IsUserRole]


class TaskListMineView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsUserRole]

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user).order_by('-created_at')


class TaskListAssignedView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsManagerRole]

    def get_queryset(self):
        return Task.objects.filter(assigned_manager=self.request.user).order_by('-created_at')


class TaskStatusUpdateView(generics.UpdateAPIView):
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [IsManagerRole]
    http_method_names = ['patch']

    def get_queryset(self):
        return Task.objects.filter(assigned_manager=self.request.user)

    def perform_update(self, serializer):
        from tasks.email_tasks import send_task_status_email
        task = serializer.save()
        send_task_status_email.delay(
            task_id=task.id,
            task_title=task.title,
            new_status=task.status,
            recipient_email=task.created_by.email,
            recipient_name=task.created_by.username,
        )


class AdminTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAdminRole]
    queryset = Task.objects.all().order_by('-created_at')


class AdminOverviewView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        tasks_by_status = {
            item['status']: item['count']
            for item in Task.objects.values('status').annotate(count=Count('id'))
        }
        for s in ['PENDING', 'APPROVED', 'REJECTED']:
            tasks_by_status.setdefault(s, 0)

        users_by_role = {
            item['role']: item['count']
            for item in User.objects.values('role').annotate(count=Count('id'))
        }
        for r in ['ADMIN', 'MANAGER', 'USER']:
            users_by_role.setdefault(r, 0)

        return Response({
            'total_users': User.objects.count(),
            'total_tasks': Task.objects.count(),
            'tasks_by_status': tasks_by_status,
            'users_by_role': users_by_role,
        })
