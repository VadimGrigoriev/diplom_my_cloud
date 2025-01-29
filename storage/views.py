from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import status
from .models import CustomUser, File, FileToken
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    FileSerializer,
    AdminUserSerializer,
    CustomTokenObtainPairSerializer,
    FileTokenSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.timezone import now, timedelta
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.http import FileResponse
from pathlib import Path
from urllib.parse import quote
import os


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # проверка уникальности имени пользователя и email
            if CustomUser.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'error': 'Логин уже занят'}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({'error': 'Email уже используется'}, status=status.HTTP_400_BAD_REQUEST)

            # Создание пользователя
            user = serializer.save()
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                }
            }, status=status.HTTP_201_CREATED)

        # Возвращаем ошибки валидации
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем файлы только для текущего пользователя
        return File.objects.filter(user=self.request.user)

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

        # Обновляем дату последнего скачивания
        file_instance.last_downloaded = now()
        file_instance.save()

        # Кодируем имя файла для корректного отображения в браузере
        encoded_filename = quote(file_instance.original_name)

        # Устанавливаем корректный заголовок Content-Disposition
        response = FileResponse(file_path.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response

    @action(detail=True, methods=['post'], url_path='generate-token')
    def generate_token(self, request, pk=None):
        """Генерация временной ссылки"""
        file_instance = self.get_object()
        user = request.user
        expires_at = now() + timedelta(minutes=10)  # Срок действия токена 10 минут

        token = FileToken.objects.create(
            file=file_instance,
            user=user,
            expires_at=expires_at
        )

        serializer = FileTokenSerializer(token, context={'request': request})  # Передаем request в контекст
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='download-temp/(?P<token>[^/]+)', permission_classes=[AllowAny])
    def download_temp(self, request, token=None):
        """Скачивание файла по временной ссылке без авторизации"""
        try:
            token_instance = FileToken.objects.get(token=token)
            if not token_instance.is_valid():
                return Response({"error": "Срок действия ссылки истек."}, status=status.HTTP_400_BAD_REQUEST)

            file_instance = token_instance.file
            file_path = Path(settings.MEDIA_ROOT) / file_instance.unique_name

            if not file_path.exists():
                return Response({"error": "Файл не найден"}, status=status.HTTP_404_NOT_FOUND)

            # Обновляем дату последнего скачивания
            file_instance.last_downloaded = now()
            file_instance.save()

            # Кодируем имя файла для корректного отображения в браузере
            encoded_filename = quote(file_instance.original_name)

            # Формируем ответ с файлом
            response = FileResponse(file_path.open('rb'), as_attachment=True)
            response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
            return response
        except FileToken.DoesNotExist:
            return Response({"error": "Токен недействителен или не существует."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    

class VerifyUserView(APIView):
    """Проверяет username и full_name перед сменой пароля."""

    def post(self, request):
        username = request.data.get("username")
        full_name = request.data.get("full_name", "").strip()

        if not username:
            return Response({"error": "Поле 'username' обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(username=username)

            # Если full_name задан, проверяем его совпадение
            if full_name and user.full_name != full_name:
                return Response({"error": "Полное имя не совпадает."}, status=status.HTTP_400_BAD_REQUEST)

            # Данные пользователя корректны
            return Response({"success": True}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "Пользователь с таким username не найден."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    """Меняет пароль пользователя."""

    def post(self, request):
        username = request.data.get("username")
        new_password = request.data.get("new_password")

        if not username or not new_password:
            return Response({"error": "Необходимо указать 'username' и 'new_password'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(username=username)
            user.password = make_password(new_password)  # Хешируем новый пароль
            user.save()

            return Response({"message": "Пароль успешно изменён."}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "Пользователь с таким username не найден."}, status=status.HTTP_404_NOT_FOUND)