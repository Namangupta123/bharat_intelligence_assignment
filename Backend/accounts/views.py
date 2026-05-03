import re
import secrets
import random
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ProfileEmailUpdateSerializer,
    ProfilePasswordUpdateSerializer,
    InviteUserSerializer,
)
from .permissions import IsAdminRole, IsUserOrManagerRole

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    queryset = User.objects.all().order_by('date_joined')


class ManagerListView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(role='MANAGER').order_by('username')


class ProfileEmailUpdateView(UpdateAPIView):
    serializer_class = ProfileEmailUpdateSerializer
    permission_classes = [IsUserOrManagerRole]
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user


class ProfilePasswordUpdateView(APIView):
    permission_classes = [IsUserOrManagerRole]

    def post(self, request):
        serializer = ProfilePasswordUpdateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


def _generate_unique_username(base_name, role_suffix):
    for _ in range(10):
        unique_id = random.randint(1000, 9999)
        username = f"{base_name}{unique_id}_{role_suffix}"
        if not User.objects.filter(username=username).exists():
            return username
    raise ValueError("Could not generate a unique username after 10 attempts.")


class InviteUserView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        role = serializer.validated_data['role']

        local_part = email.split('@')[0]
        base_name = re.sub(r'[^a-z0-9]', '', local_part.lower()) or 'user'

        role_suffix = 'manager' if role == 'MANAGER' else 'user'
        username = _generate_unique_username(base_name, role_suffix)
        temp_password = secrets.token_urlsafe(9)

        User.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            role=role,
        )

        from accounts.email_tasks import send_invitation_email
        send_invitation_email.delay(
            username=username,
            temp_password=temp_password,
            recipient_email=email,
            role=role,
        )

        return Response(
            {"detail": "User invited successfully.", "username": username, "role": role},
            status=status.HTTP_201_CREATED,
        )
