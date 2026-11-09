from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Editora(models.Model):
    nome = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nome


class Autor(models.Model):
    nome = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=250)

    edicao = models.CharField(max_length=30, blank=True)
    ano = models.PositiveSmallIntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, blank=True)
    editora = models.ForeignKey(Editora, on_delete=models.PROTECT, null=True, blank=True)

    autores = models.ManyToManyField(Autor, blank=True)

    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # ISBN vazio vira NULL, senão dois livros sem ISBN ("") violam o unique
        self.isbn = (self.isbn or "").strip() or None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Exemplar(models.Model):
    class Situacao(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        EMPRESTADO = "emprestado", "Emprestado"
        PERDIDO = "perdido", "Perdido"
        DANIFICADO = "danificado", "Danificado"

    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name="exemplares")
    tombo = models.CharField(max_length=30, unique=True)
    localizacao = models.CharField(max_length=100, blank=True)
    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.DISPONIVEL,
    )
    observacao = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'exemplares'

    def __str__(self):
        return self.tombo
