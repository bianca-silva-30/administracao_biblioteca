from rest_framework.routers import DefaultRouter

from config.urls import urlpatterns
from .views import (
    CategoriaViewSet, EditoraViewSet, AutorViewSet,
    LivroViewSet, ExemplarViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet)
router.register("editoras", EditoraViewSet)
router.register("autores", AutorViewSet)
router.register("livros", LivroViewSet)
router.register("exemplares", ExemplarViewSet)

urlpatterns = router.urls
