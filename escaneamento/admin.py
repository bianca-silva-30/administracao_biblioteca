from django.contrib import admin

from .models import SessaoEscaneamento


@admin.register(SessaoEscaneamento)
class SessaoEscaneamentoAdmin(admin.ModelAdmin):
    list_display = ("token", "status", "criado_por", "criada_em", "expira_em")
    readonly_fields = ("token", "criada_em")