from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from .models import CustomUser, File
from .serializers import UserSerializer, RegisterSerializer, FileSerializer, AdminUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils.timezone import now
from django.conf import settings
from django.http import FileResponse
from pathlib import Path
import os


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Передаем текущий запрос в контекст сериализотора
        return {'request': self.request}

    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Обработка массовой загрузки файлов"""
        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "Файлы не предоставлены."}, status=status.HTTP_400_BAD_REQUEST)

        # Создание папки пользователя
        user_folder = os.path.join(settings.MEDIA_ROOT, f"user_{request.user.id}")
        os.makedirs(user_folder, exist_ok=True)

        # Обработка каждого файла
        created_files = []
        for uploaded_file in files:
            unique_name = f"{now().timestamp()}_{uploaded_file.name}"
            file_path = os.path.join(user_folder, unique_name)

            # Сохраняем файл на диск
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Создаем запись в базе данных
            file_instance = File.objects.create(
                user=request.user,
                original_name=uploaded_file.name,
                unique_name=os.path.join(f"user_{request.user.id}", unique_name),
                size=uploaded_file.size,
            )
            created_files.append(file_instance)

        # Возвращаем информацию о загруженных файлах
        serializer = self.get_serializer(created_files, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='rename')
    def rename_file(self, request, pk=None):
        """Переименование файла"""
        file_instance = self.get_object()
        new_name = request.data.get('original_name')

        if not new_name:
            return Response({"error": "Новое имя файла не указано."}, status=status.HTTP_400_BAD_REQUEST)

        file_instance.original_name = new_name
        file_instance.save()
        return Response({"message": "Имя файла обновлено", "original_name": file_instance.original_name})

    @action(detail=True, methods=['patch'], url_path='comment')
    def update_comment(self, request, pk=None):
        """Добавление или изменение комментария"""
        file_instance = self.get_object()
        new_comment = request.data.get('comment', '')

        file_instance.comment = new_comment
        file_instance.save()
        return Response({"message": "Комментарий обновлен", "comment": file_instance.comment})

    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, pk=None):
        """Скачивание файла"""
        file_instance = self.get_object()
        file_path = Path(settings.MEDIA_ROOT) / file_instance.unique_name

        # Логируем путь для проверки
        print(f"Пытаемся найти файл по пути: {file_path}")

        if not file_path.exists():
            return Response({"error": "Файл не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Устанавливаем корректный заголовок Content-Disposition
        response = FileResponse(file_path.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{file_instance.original_name}"
        return response


class AdminUserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]  # Доступ только администраторам

    @action(detail=True, methods=['patch'], url_path='set-admin')
    def set_admin(self, request, pk=None):
        """Назначение/снятие роли администратора"""
        user = self.get_object()
        is_admin = request.data.get('is_admin', False)

        user.is_superuser = is_admin
        user.save()
        return Response({'message': 'Роль обновлена', 'is_admin': user.is_superuser})
    
