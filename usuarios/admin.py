from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nome", "matricula", "vinculo", "curso", "ativo")
    list_filter = ("vinculo", "ativo")
    search_fields = ("nome", "matricula", "email")