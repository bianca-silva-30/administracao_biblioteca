from django.contrib import admin
from .models import Categoria, Editora, Autor, Livro, Exemplar

admin.site.register(Categoria)
admin.site.register(Editora)
admin.site.register(Autor)
admin.site.register(Livro)
admin.site.register(Exemplar)
