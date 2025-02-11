from rest_framework import serializers
from storage.models import CustomUser, File


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения статуса администратора"""
    class Meta:
        model = CustomUser
        fields = ['is_admin']


class AdminFileSerializer(serializers.ModelSerializer):
    """Сериализатор для админов: просмотр и удаление файлов"""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = File
        fields = ['id', 'original_name', 'size', 'uploaded_at', 'last_downloaded', 'comment', 'user_username']
