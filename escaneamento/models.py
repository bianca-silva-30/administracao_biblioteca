import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def expiracao_padrao():
    return timezone.now() + timedelta(minutes=10)


class SessaoEscaneamento(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO = "aguardando", "Aguardando foto"
        ENVIADA = "enviada", "Foto enviada"
        PROCESSADA = "processada", "Processada"
        ERRO = "erro", "Erro"

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AGUARDANDO
    )
    imagem = models.ImageField(upload_to="capas/", blank=True)
    resultado = models.JSONField(default=dict, blank=True)
    erro = models.CharField(max_length=300, blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessoes_escaneamento",
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(default=expiracao_padrao)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "sessão de escaneamento"
        verbose_name_plural = "sessões de escaneamento"

    @property
    def expirada(self):
        return timezone.now() >= self.expira_em

    def __str__(self):
        return f"{self.token} ({self.status})"