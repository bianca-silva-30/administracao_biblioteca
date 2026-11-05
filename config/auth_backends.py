from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOuMatriculaBackend(ModelBackend):
    """Permite entrar com e-mail OU matrícula (o username) mais a senha."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        User = get_user_model()
        encontrados = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        )
        # Se não achar nenhum, ou achar mais de um (e-mail repetido), recusa
        if encontrados.count() != 1:
            return None

        usuario = encontrados.first()
        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
