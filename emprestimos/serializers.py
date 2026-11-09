from rest_framework import serializers

from acervo.models import Exemplar
from usuarios.models import Usuario
from .models import Emprestimo


class EmprestimoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source="usuario.nome", read_only=True)
    usuario_matricula = serializers.CharField(source="usuario.matricula", read_only=True)
    exemplar_tombo = serializers.CharField(source="exemplar.tombo", read_only=True)
    livro_titulo = serializers.CharField(source="exemplar.livro.titulo", read_only=True)

    status = serializers.CharField(read_only=True)
    atrasado = serializers.BooleanField(source="esta_atrasado", read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)

    class Meta:
        model = Emprestimo
        fields = [
            "id", "usuario", "usuario_nome", "usuario_matricula",
            "exemplar", "exemplar_tombo", "livro_titulo",
            "data_emprestimo", "data_prevista", "data_devolucao",
            "renovacoes", "estado_devolucao", "observacao",
            "status", "atrasado", "dias_atraso",
        ]
        read_only_fields = fields


class NovoEmprestimoSerializer(serializers.Serializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    exemplar = serializers.PrimaryKeyRelatedField(queryset=Exemplar.objects.all())


class DevolucaoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=Emprestimo.EstadoDevolucao.choices,
        default=Emprestimo.EstadoDevolucao.BOM,
    )
    observacao = serializers.CharField(required=False, allow_blank=True, default="")
