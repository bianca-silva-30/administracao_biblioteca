from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from acervo.models import Exemplar
from usuarios.models import Usuario
from .models import Emprestimo


def registrar_emprestimo(usuario, exemplar):
    cfg = settings.BIBLIOTECA
    hoje = timezone.localdate()

    with transaction.atomic():
        exemplar = Exemplar.objects.select_for_update().get(pk=exemplar.pk)
        usuario = Usuario.objects.select_for_update().get(pk=usuario.pk)

        if not usuario.ativo:
            raise ValidationError({"usuario": "Usuário inativo."})
        if not exemplar.livro.ativo:
            raise ValidationError({"exemplar": "O livro está inativo no acervo."})
        if exemplar.situacao != Exemplar.Situacao.DISPONIVEL:
            raise ValidationError({
                "exemplar": f"Exemplar indisponível (situação: {exemplar.get_situacao_display()})."
            })

        abertos = Emprestimo.objects.ativos().filter(usuario=usuario)
        if cfg["BLOQUEAR_COM_ATRASO"] and abertos.filter(data_prevista__lt=hoje).exists():
            raise ValidationError({"usuario": "O usuário tem empréstimo em atraso."})
        if abertos.count() >= cfg["MAX_EMPRESTIMOS_SIMULTANEOS"][usuario.vinculo]:
            raise ValidationError({"usuario": "Limite de empréstimos simultâneos atingido."})

        prazo = cfg["PRAZO_EMPRESTIMO_DIAS"][usuario.vinculo]
        emprestimo = Emprestimo.objects.create(
            usuario=usuario,
            exemplar=exemplar,
            data_prevista=hoje + timedelta(days=prazo),
        )
        exemplar.situacao = Exemplar.Situacao.EMPRESTADO
        exemplar.save(update_fields=["situacao", "atualizado_em"])

    return emprestimo


def registrar_devolucao(emprestimo, estado="bom", observacao=""):
    with transaction.atomic():
        emprestimo = Emprestimo.objects.select_for_update().get(pk=emprestimo.pk)
        if emprestimo.devolvido:
            raise ValidationError("Este empréstimo já foi devolvido.")

        exemplar = Exemplar.objects.select_for_update().get(pk=emprestimo.exemplar_id)

        emprestimo.data_devolucao = timezone.now()
        emprestimo.estado_devolucao = estado
        if observacao:
            emprestimo.observacao = observacao
        emprestimo.save()

        exemplar.situacao = {
            Emprestimo.EstadoDevolucao.BOM: Exemplar.Situacao.DISPONIVEL,
            Emprestimo.EstadoDevolucao.DANIFICADO: Exemplar.Situacao.DANIFICADO,
            Emprestimo.EstadoDevolucao.PERDIDO: Exemplar.Situacao.PERDIDO,
        }[estado]
        exemplar.save(update_fields=["situacao", "atualizado_em"])

    return emprestimo


def renovar_emprestimo(emprestimo):
    cfg = settings.BIBLIOTECA

    with transaction.atomic():
        emprestimo = Emprestimo.objects.select_for_update().get(pk=emprestimo.pk)
        if emprestimo.devolvido:
            raise ValidationError("Este empréstimo já foi devolvido.")
        if emprestimo.esta_atrasado:
            raise ValidationError("Empréstimo em atraso não pode ser renovado.")
        if emprestimo.renovacoes >= cfg["MAX_RENOVACOES"]:
            raise ValidationError("Limite de renovações atingido.")
        # Quando existir o app de reservas, bloquear aqui se houver fila para o livro.

        prazo = cfg["PRAZO_EMPRESTIMO_DIAS"][emprestimo.usuario.vinculo]
        emprestimo.data_prevista = timezone.localdate() + timedelta(days=prazo)
        emprestimo.renovacoes += 1
        emprestimo.save(update_fields=["data_prevista", "renovacoes"])

    return emprestimo