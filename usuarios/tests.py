from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Usuario


class UsuarioAPITests(APITestCase):
    def setUp(self):
        self.bibliotecario = get_user_model().objects.create_user(
            username="bib01", password="senha-forte-123"
        )
        self.client.force_authenticate(self.bibliotecario)

    def test_exige_login(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 401)

    def test_cria_aluno_com_curso(self):
        r = self.client.post("/api/usuarios/", {
            "nome": "Ana Souza", "matricula": "2024001",
            "vinculo": "aluno", "curso": "Sistemas de Informação",
        })
        self.assertEqual(r.status_code, 201)

    def test_aluno_sem_curso_e_recusado(self):
        r = self.client.post("/api/usuarios/", {
            "nome": "Ana Souza", "matricula": "2024001", "vinculo": "aluno",
        })
        self.assertEqual(r.status_code, 400)
        self.assertIn("curso", r.data)

    def test_professor_nao_precisa_de_curso(self):
        r = self.client.post("/api/usuarios/", {
            "nome": "Carlos Lima", "matricula": "P100", "vinculo": "professor",
        })
        self.assertEqual(r.status_code, 201)

    def test_matricula_duplicada(self):
        Usuario.objects.create(nome="A", matricula="1", vinculo="colaborador")
        r = self.client.post("/api/usuarios/", {
            "nome": "B", "matricula": "1", "vinculo": "colaborador",
        })
        self.assertEqual(r.status_code, 400)

    def test_busca_e_filtro_de_ativos(self):
        Usuario.objects.create(nome="Maria", matricula="10", vinculo="colaborador")
        Usuario.objects.create(nome="Marcos", matricula="11", vinculo="colaborador", ativo=False)
        r = self.client.get("/api/usuarios/?search=Mar&ativo=true")
        self.assertEqual(r.data["count"], 1)

    def test_nao_permite_delete(self):
        u = Usuario.objects.create(nome="A", matricula="1", vinculo="colaborador")
        self.assertEqual(self.client.delete(f"/api/usuarios/{u.id}/").status_code, 405)

    def test_desativar(self):
        u = Usuario.objects.create(nome="A", matricula="1", vinculo="colaborador")
        r = self.client.patch(f"/api/usuarios/{u.id}/", {"ativo": False})
        self.assertEqual(r.status_code, 200)
        u.refresh_from_db()
        self.assertFalse(u.ativo)