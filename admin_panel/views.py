from rest_framework import generics, permissions
from storage.models import CustomUser, File
from storage.serializers import AdminUserSerializer
from .serializers import AdminUserUpdateSerializer, AdminFileSerializer
from django.db.models import Count, Sum


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AdminUserListView(generics.ListAPIView):
    """Получение списка пользователей с их файлами"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        return CustomUser.objects.annotate(
            file_count=Count('files'),
            total_file_size=Sum('files__size')
        )


class AdminUserUpdateView(generics.UpdateAPIView):
    """Изменение статуса администратора"""
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdminUserDeleteView(generics.DestroyAPIView):
    """Удаление пользователя"""
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AdminFileListView(generics.ListAPIView):
    """Админ может видеть все файлы конкретного пользователя"""
    serializer_class = AdminFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтруем файлы по user_id из URL"""
        user_id = self.kwargs.get('user_id')
        return File.objects.filter(user_id=user_id) if user_id else File.objects.none()


class AdminFileDeleteView(generics.DestroyAPIView):
    """Админ может удалять файлы пользователей"""
    queryset = File.objects.all()
    serializer_class = AdminFileSerializer
    permission_classes = [permissions.IsAuthenticated]
