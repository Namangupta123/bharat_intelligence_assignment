from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    assigned_manager_username = serializers.CharField(
        source='assigned_manager.username', read_only=True, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'created_by', 'created_by_username',
            'assigned_manager', 'assigned_manager_username',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'created_by', 'created_by_username',
            'assigned_manager_username', 'created_at', 'updated_at',
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_manager']

    def validate_assigned_manager(self, value):
        if value is not None and value.role != 'MANAGER':
            raise serializers.ValidationError(
                "assigned_manager must have the MANAGER role."
            )
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value):
        if value not in ['APPROVED', 'REJECTED']:
            raise serializers.ValidationError(
                "Managers can only set status to APPROVED or REJECTED."
            )
        return value
