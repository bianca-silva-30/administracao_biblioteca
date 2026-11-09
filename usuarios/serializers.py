from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    vinculo_nome = serializers.CharField(source="get_vinculo_display", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id", "nome", "matricula", "vinculo", "vinculo_nome", "curso",
            "email", "telefone", "ativo", "criado_em",
        ]
        read_only_fields = ["criado_em"]

    def validate_matricula(self, value):
        return value.strip()

    def validate(self, attrs):
        # No PATCH, vínculo/curso podem não vir: completa com o que já está salvo
        vinculo = attrs.get("vinculo", getattr(self.instance, "vinculo", None))
        curso = attrs.get("curso", getattr(self.instance, "curso", ""))
        if vinculo == Usuario.Vinculo.ALUNO and not (curso or "").strip():
            raise serializers.ValidationError({"curso": "Informe o curso do aluno."})
        return attrs