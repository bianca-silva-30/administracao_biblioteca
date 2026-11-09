from rest_framework import serializers
from django.db import transaction
from .models import Categoria, Editora, Autor, Livro, Exemplar


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = '__all__'


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'


class ExemplarSerializer(serializers.ModelSerializer):
    livro_titulo = serializers.StringRelatedField(source='livro', read_only=True)

    class Meta:
        model = Exemplar
        fields = [
            'id', 'livro', 'livro_titulo', 'tombo',
            'localizacao', 'situacao', 'observacao', 'atualizado_em',
        ]

    def validate_situacao(self, value):
        ja_emprestado = self.instance is not None and self.instance.situacao == Exemplar.Situacao.EMPRESTADO
        if value == Exemplar.Situacao.EMPRESTADO and not ja_emprestado:
            raise serializers.ValidationError(
                "A situação 'emprestado' é definida apenas pelo registro de empréstimo."
            )
        return value


class LivroSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.StringRelatedField(source="categoria", read_only=True)
    editora_nome = serializers.StringRelatedField(source="editora", read_only=True)
    autores_nomes = serializers.StringRelatedField(source="autores", many=True, read_only=True)

    exemplares = ExemplarSerializer(many=True, read_only=True)

    total_exemplares = serializers.SerializerMethodField()
    exemplares_disponiveis = serializers.SerializerMethodField()

    # Só para escrita: o front manda nomes e não precisa conhecer ids
    categoria_texto = serializers.CharField(write_only=True, required=False, allow_blank=True)
    autor_texto = serializers.CharField(write_only=True, required=False, allow_blank=True)
    quantidade_exemplares = serializers.IntegerField(
        write_only=True, required=False, min_value=0, max_value=200
    )

    class Meta:
        model = Livro
        fields = [
            "id", "titulo", "edicao", "ano", "isbn", "ativo",
            "categoria", "categoria_nome", "categoria_texto",
            "editora", "editora_nome",
            "autores", "autores_nomes", "autor_texto",
            "quantidade_exemplares",
            "total_exemplares", "exemplares_disponiveis", "exemplares",
        ]

    # Usa o prefetch_related da view: contar em Python evita uma consulta por livro
    # noinspection PyUnresolvedReferences
    def get_total_exemplares(self, obj):
        return len(obj.exemplares.all())

    # noinspection PyUnresolvedReferences
    def get_exemplares_disponiveis(self, obj):
        return sum(
            1 for e in obj.exemplares.all()
            if e.situacao == Exemplar.Situacao.DISPONIVEL
        )

    def validate_isbn(self, value):
        return (value or "").strip() or None

    @staticmethod
    def _obter_ou_criar(modelo, nome):
        existente = modelo.objects.filter(nome__iexact=nome).first()
        return existente or modelo.objects.create(nome=nome)

    def _resolver_textos(self, dados):
        categoria = (dados.pop("categoria_texto", "") or "").strip()
        autor = (dados.pop("autor_texto", "") or "").strip()
        if categoria:
            dados["categoria"] = self._obter_ou_criar(Categoria, categoria)
        if autor:
            dados["autores"] = [self._obter_ou_criar(Autor, autor)]

    @transaction.atomic
    def create(self, validated_data):
        quantidade = validated_data.pop("quantidade_exemplares", 0)
        self._resolver_textos(validated_data)
        livro = super().create(validated_data)
        Exemplar.objects.bulk_create([
            Exemplar(livro=livro, tombo=f"LIV{livro.pk:04d}-{n:02d}")
            for n in range(1, quantidade + 1)
        ])
        return livro

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop("quantidade_exemplares", None)  # exemplares extras: pela rota /api/exemplares/
        self._resolver_textos(validated_data)
        return super().update(instance, validated_data)