from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SessaoEscaneamento
from .serializers import SessaoEscaneamentoSerializer, UploadImagemSerializer
from .services import analisar_capa


class CriarSessaoView(APIView):
    def post(self, request):
        sessao = SessaoEscaneamento.objects.create(criado_por=request.user)
        dados = SessaoEscaneamentoSerializer(sessao).data
        return Response(dados, status=status.HTTP_201_CREATED)


class StatusSessaoView(APIView):
    def get(self, request, token):
        sessao = get_object_or_404(
            SessaoEscaneamento, token=token, criado_por=request.user
        )
        return Response(SessaoEscaneamentoSerializer(sessao).data)


class EnviarImagemView(APIView):
    authentication_classes = []  # o celular não faz login: o token da sessão é a credencial
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request, token):
        sessao = get_object_or_404(SessaoEscaneamento, token=token)

        if sessao.expirada:
            return Response(
                {"detail": "Sessão expirada."}, status=status.HTTP_410_GONE
            )
        if sessao.status != SessaoEscaneamento.Status.AGUARDANDO:
            return Response(
                {"detail": "Esta sessão já recebeu uma imagem."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = UploadImagemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sessao.imagem = serializer.validated_data["imagem"]
        sessao.status = SessaoEscaneamento.Status.ENVIADA
        sessao.save()

        try:
            sessao.resultado = analisar_capa(sessao)
            sessao.status = SessaoEscaneamento.Status.PROCESSADA
        except Exception:
            sessao.status = SessaoEscaneamento.Status.ERRO
            sessao.erro = "Não foi possível analisar a capa."
        sessao.save()

        return Response({"status": sessao.status})
