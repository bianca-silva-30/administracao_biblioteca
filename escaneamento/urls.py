from django.urls import path

from .views import CriarSessaoView, EnviarImagemView, StatusSessaoView

urlpatterns = [
    path("escaneamento/sessoes/", CriarSessaoView.as_view()),
    path("escaneamento/sessoes/<uuid:token>/", StatusSessaoView.as_view()),
    path("escaneamento/sessoes/<uuid:token>/imagem/", EnviarImagemView.as_view()),
]