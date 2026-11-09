from rest_framework import filters, mixins, viewsets
from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Sem DELETE de propósito: para tirar alguém de circulação, use ativo=false."""

    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome", "matricula", "email", "curso"]

    def get_queryset(self):
        qs = Usuario.objects.order_by("nome")
        # /api/usuarios/?vinculo=aluno&ativo=true
        vinculo = self.request.query_params.get("vinculo")
        ativo = self.request.query_params.get("ativo")
        if vinculo:
            qs = qs.filter(vinculo=vinculo)
        if ativo in ("true", "false"):
            qs = qs.filter(ativo=(ativo == "true"))
        return qs