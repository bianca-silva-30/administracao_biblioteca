from django.db import models
from django.utils import timezone


class EmprestimoQuerySet(models.QuerySet):
    def ativos(self):
        return self.filter(data_devolucao__isnull=True)

    def atrasados(self):
        return self.ativos().filter(data_prevista__lt=timezone.localdate())


class Emprestimo(models.Model):
    class EstadoDevolucao(models.TextChoices):
        BOM = "bom", "Bom estado"
        DANIFICADO = "danificado", "Danificado"
        PERDIDO = "perdido", "Perdido"

    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.PROTECT, related_name="emprestimos"
    )
    exemplar = models.ForeignKey(
        "acervo.Exemplar", on_delete=models.PROTECT, related_name="emprestimos"
    )

    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_prevista = models.DateField()
    data_devolucao = models.DateTimeField(null=True, blank=True)

    renovacoes = models.PositiveSmallIntegerField(default=0)
    estado_devolucao = models.CharField(
        max_length=20, choices=EstadoDevolucao.choices, blank=True
    )
    observacao = models.TextField(blank=True)

    objects = EmprestimoQuerySet.as_manager()

    class Meta:
        constraints = [
            # O próprio banco impede dois empréstimos abertos do mesmo exemplar
            models.UniqueConstraint(
                fields=["exemplar"],
                condition=models.Q(data_devolucao__isnull=True),
                name="um_emprestimo_aberto_por_exemplar",
            )
        ]

    @property
    def devolvido(self):
        return self.data_devolucao is not None

    # O atraso é calculado, não gravado: nunca fica desatualizado
    @property
    def dias_atraso(self):
        if self.devolvido:
            return 0
        return max((timezone.localdate() - self.data_prevista).days, 0)

    @property
    def esta_atrasado(self):
        return self.dias_atraso > 0

    @property
    def status(self):
        if self.devolvido:
            return "devolvido"
        return "atrasado" if self.esta_atrasado else "ativo"

    def __str__(self):
        return f"{self.usuario} - {self.exemplar}"
