from rest_framework import viewsets, filters
from .models import Categoria, Editora, Autor, Livro, Exemplar
from .serializers import (
    CategoriaSerializer, EditoraSerializer, AutorSerializer,
    LivroSerializer, ExemplarSerializer,
)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.order_by("nome")
    serializer_class = CategoriaSerializer


class EditoraViewSet(viewsets.ModelViewSet):
    queryset = Editora.objects.order_by("nome")
    serializer_class = EditoraSerializer


class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.order_by("nome")
    serializer_class = AutorSerializer


class LivroViewSet(viewsets.ModelViewSet):
    # select_related/prefetch_related evitam consultas repetidas ao banco
    queryset = (
        Livro.objects
        .select_related("categoria", "editora")
        .prefetch_related("autores", "exemplares")
        .order_by("titulo")
    )
    serializer_class = LivroSerializer

    # Busca: /api/livros/?search=texto (PBI-9)
    filter_backends = [filters.SearchFilter]
    search_fields = ["titulo", "isbn", "autores__nome", "categoria__nome", ]


class ExemplarViewSet(viewsets.ModelViewSet):
    queryset = Exemplar.objects.select_related("livro").order_by("tombo")
    serializer_class = ExemplarSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ["tombo", "livro__titulo"]

    def get_queryset(self):
        qs = super().get_queryset()
        livro = self.request.query_params.get("livro")
        situacao = self.request.query_params.get("situacao")
        if livro:
            qs = qs.filter(livro_id=livro)
        if situacao:
            qs = qs.filter(situacao=situacao)
        return qs
