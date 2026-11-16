from rest_framework import serializers

from .models import SessaoEscaneamento


class SessaoEscaneamentoSerializer(serializers.ModelSerializer):
    expirada = serializers.BooleanField(read_only=True)

    class Meta:
        model = SessaoEscaneamento
        fields = ["token", "status", "resultado", "erro", "expira_em", "expirada"]
        read_only_fields = fields


class UploadImagemSerializer(serializers.Serializer):
    imagem = serializers.ImageField()

    def validate_imagem(self, arquivo):
        if arquivo.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("A imagem deve ter no máximo 10 MB.")
        return arquivo
