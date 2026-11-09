from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EmprestimoViewSet, painel

router = DefaultRouter()
router.register("emprestimos", EmprestimoViewSet, basename="emprestimo")

urlpatterns = [
    path("painel/", painel),
] + router.urls