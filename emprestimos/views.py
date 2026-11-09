from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from . import services
from .models import Emprestimo
from .serializers import (
    DevolucaoSerializer, EmprestimoSerializer, NovoEmprestimoSerializer,
)


class EmprestimoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/emprestimos/?status=ativos|atrasados|devolvidos&usuario=ID&search=texto
    POST /api/emprestimos/                  {usuario, exemplar}
    POST /api/emprestimos/{id}/devolver/    {estado, observacao}
    POST /api/emprestimos/{id}/renovar/
    """

    serializer_class = EmprestimoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "usuario__nome", "usuario__matricula",
        "exemplar__tombo", "exemplar__livro__titulo",
    ]

    def get_queryset(self):
        qs = Emprestimo.objects.select_related("usuario", "exemplar__livro")
        params = self.request.query_params

        situacao = params.get("status")
        if situacao == "ativos":
            qs = qs.ativos()
        elif situacao == "atrasados":
            qs = qs.atrasados()
        elif situacao == "devolvidos":
            qs = qs.filter(data_devolucao__isnull=False)

        if params.get("usuario"):
            qs = qs.filter(usuario_id=params["usuario"])
        if params.get("matricula"):
            qs = qs.filter(usuario__matricula=params["matricula"])
        if params.get("exemplar"):
            qs = qs.filter(exemplar_id=params["exemplar"])

        # Mais atrasados primeiro, depois os mais recentes
        return qs.order_by("data_prevista", "-id") if situacao in ("ativos", "atrasados") \
            else qs.order_by("-data_emprestimo")

    def create(self, request, *args, **kwargs):
        entrada = NovoEmprestimoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        emprestimo = services.registrar_emprestimo(**entrada.validated_data)
        return Response(EmprestimoSerializer(emprestimo).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def devolver(self, request, pk=None):
        entrada = DevolucaoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        emprestimo = services.registrar_devolucao(self.get_object(), **entrada.validated_data)
        return Response(EmprestimoSerializer(emprestimo).data)

    @action(detail=True, methods=["post"])
    def renovar(self, request, pk=None):
        emprestimo = services.renovar_emprestimo(self.get_object())
        return Response(EmprestimoSerializer(emprestimo).data)


@api_view(["GET"])
def painel(request):
    hoje = timezone.localdate()
    ativos = Emprestimo.objects.ativos()
    return Response({
        "devolucoes_hoje": ativos.filter(data_prevista=hoje).count(),
        "atrasados": Emprestimo.objects.atrasados().count(),
        "emprestimos_ativos": ativos.count(),
        "reservas_pendentes": 0,  # passa a ser real quando o app de reservas existir
    })