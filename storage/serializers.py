from rest_framework import serializers
from .models import CustomUser, File, FileToken
from django.utils.timezone import now
from django.conf import settings
from pathlib import Path
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username  # Добавляем username
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'is_admin']


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для админов с информацией о файлах"""
    file_count = serializers.IntegerField()
    total_file_size = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'is_admin', 'file_count', 'total_file_size']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')  # Получаем full_name или пустую строку
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=full_name
        )
        return user


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


class FileTokenSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = FileToken
        fields = ['token', 'expires_at', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/files/download-temp/{obj.token}/")
        return None


