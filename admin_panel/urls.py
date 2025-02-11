from django.urls import path
from .views import AdminUserListView, AdminUserUpdateView, AdminFileListView, AdminFileDeleteView, AdminUserDeleteView

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', AdminUserUpdateView.as_view(), name='admin-user-update'),
    path('users/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
    path('users/<int:user_id>/files/', AdminFileListView.as_view(), name='admin-user-files'),
    path('files/<int:pk>/', AdminFileDeleteView.as_view(), name='admin-file-delete'),
]