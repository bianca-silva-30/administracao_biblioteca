from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import eu

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/eu/", eu),
    path("api/", include("acervo.urls")),
    path("api/", include("usuarios.urls")),
    path("api/", include("emprestimos.urls")),
]