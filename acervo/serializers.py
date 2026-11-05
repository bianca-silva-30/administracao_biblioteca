from rest_framework import serializers
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

    class Meta:
        model = Livro
        fields = [
            "id", "titulo", "edicao", "ano", "isbn", "ativo",
            "categoria", "categoria_nome",
            "editora", "editora_nome",
            "autores", "autores_nomes",
            "total_exemplares", "exemplares_disponiveis", "exemplares",
        ]

    # noinspection PyUnresolvedReferences
    def get_total_exemplares(self, obj):
        return obj.exemplares.count()

    # noinspection PyUnresolvedReferences
    def get_exemplares_disponiveis(self, obj):
        return obj.exemplares.filter(situacao=Exemplar.Situacao.DISPONIVEL).count()

