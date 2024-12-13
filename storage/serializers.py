from rest_framework import serializers
from .models import CustomUser, File
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.conf import settings
from pathlib import Path
from django.db.models import Sum
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'is_admin']


class AdminUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_superuser')  # Для работы с флагом администратора
    file_count = serializers.SerializerMethodField()
    total_file_size = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_admin', 'file_count', 'total_file_size']

    def get_file_count(self, obj):
        return obj.files.count()  # Количество файлов у пользователя

    def get_total_file_size(self, obj):
        result = obj.files.aggregate(total_size=Sum('size'))
        return result['total_size'] or 0  # Общий размер файлов


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'full_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = File
        fields = ['id', 'file', 'original_name', 'unique_name', 'size', 'uploaded_at', 'last_downloaded', 'comment']
        read_only_fields = ['original_name', 'unique_name', 'size', 'uploaded_at', 'last_downloaded']

    def create(self, validated_data):
        # Получаем загружаемый файл
        uploaded_file = validated_data.pop('file')
        request = self.context.get('request')

        # Проверяем наличие пользователя в контексте
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Необходимо указать пользователя.")

        # Генерация пути пользователя
        user_folder = Path(f"user_{request.user.id}")
        unique_name = user_folder / f"{now().timestamp()}_{uploaded_file.name}"
        file_path = Path(settings.MEDIA_ROOT) / unique_name

        # Сохраняем файл на сервере
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Создаем папку, если её нет
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Заполняет поля модели
        return File.objects.create(
            user=request.user,
            original_name=uploaded_file.name,
            unique_name=str(unique_name).replace("\\", "/"),  # Преобразуем путь
            size=uploaded_file.size,
            **validated_data
        )

