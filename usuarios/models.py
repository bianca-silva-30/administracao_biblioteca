from django.db import models


class Usuario(models.Model):
    """Pessoa que pega livros emprestados (não é o login do bibliotecário)."""

    class Vinculo(models.TextChoices):
        ALUNO = "aluno", "Aluno"
        PROFESSOR = "professor", "Professor"
        COLABORADOR = "colaborador", "Colaborador"

    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=30, unique=True)
    vinculo = models.CharField(max_length=20, choices=Vinculo.choices)
    curso = models.CharField(max_length=120, blank=True)

    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)

    # Em vez de apagar, o bibliotecário desativa: o histórico de empréstimos fica preservado
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def __str__(self):
        return f"{self.nome} ({self.matricula})"