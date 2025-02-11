from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RegisterView,
    FileViewSet,
    CustomTokenObtainPairView,
    VerifyUserView,
    ResetPasswordView,
    get_current_user
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/auth/verify-user/", VerifyUserView.as_view(), name="verify_user"),
    path("api/auth/reset-password/", ResetPasswordView.as_view(), name="reset_password"),

    path('api/auth/me/', get_current_user, name='auth-me'),
]