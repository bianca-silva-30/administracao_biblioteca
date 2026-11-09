from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from acervo.models import Exemplar, Livro
from usuarios.models import Usuario
from .models import Emprestimo


class EmprestimoAPITests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(
            get_user_model().objects.create_user(username="bib01", password="senha-forte-123")
        )
        self.usuario = Usuario.objects.create(
            nome="Ana", matricula="1", vinculo="aluno", curso="Sistemas"
        )
        self.livro = Livro.objects.create(titulo="Livro A")
        self.ex = Exemplar.objects.create(livro=self.livro, tombo="T1")

    def emprestar(self, exemplar=None, usuario=None):
        return self.client.post("/api/emprestimos/", {
            "usuario": (usuario or self.usuario).id,
            "exemplar": (exemplar or self.ex).id,
        })

    def test_emprestimo_calcula_prazo_e_marca_exemplar(self):
        r = self.emprestar()
        self.assertEqual(r.status_code, 201, r.data)
        prazo = settings.BIBLIOTECA["PRAZO_EMPRESTIMO_DIAS"]["aluno"]
        esperado = timezone.localdate() + timedelta(days=prazo)
        self.assertEqual(r.data["data_prevista"], esperado.isoformat())
        self.ex.refresh_from_db()
        self.assertEqual(self.ex.situacao, Exemplar.Situacao.EMPRESTADO)

    def test_exemplar_emprestado_nao_sai_de_novo(self):
        self.emprestar()
        outro = Usuario.objects.create(nome="Bia", matricula="2", vinculo="professor")
        self.assertEqual(self.emprestar(usuario=outro).status_code, 400)

    def test_limite_de_emprestimos_simultaneos(self):
        limite = settings.BIBLIOTECA["MAX_EMPRESTIMOS_SIMULTANEOS"]["aluno"]
        for i in range(limite):
            ex = Exemplar.objects.create(livro=self.livro, tombo=f"X{i}")
            self.assertEqual(self.emprestar(exemplar=ex).status_code, 201)
        extra = Exemplar.objects.create(livro=self.livro, tombo="EXTRA")
        self.assertEqual(self.emprestar(exemplar=extra).status_code, 400)

    def test_usuario_inativo_nao_pega_livro(self):
        self.usuario.ativo = False
        self.usuario.save()
        self.assertEqual(self.emprestar().status_code, 400)

    def test_devolucao_libera_exemplar(self):
        emp_id = self.emprestar().data["id"]
        r = self.client.post(f"/api/emprestimos/{emp_id}/devolver/", {"estado": "bom"})
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["status"], "devolvido")
        self.ex.refresh_from_db()
        self.assertEqual(self.ex.situacao, Exemplar.Situacao.DISPONIVEL)

    def test_devolucao_danificado(self):
        emp_id = self.emprestar().data["id"]
        self.client.post(f"/api/emprestimos/{emp_id}/devolver/", {"estado": "danificado"})
        self.ex.refresh_from_db()
        self.assertEqual(self.ex.situacao, Exemplar.Situacao.DANIFICADO)

    def test_nao_devolve_duas_vezes(self):
        emp_id = self.emprestar().data["id"]
        self.client.post(f"/api/emprestimos/{emp_id}/devolver/", {})
        r = self.client.post(f"/api/emprestimos/{emp_id}/devolver/", {})
        self.assertEqual(r.status_code, 400)

    def test_renovacao_e_limite(self):
        emp_id = self.emprestar().data["id"]
        for _ in range(settings.BIBLIOTECA["MAX_RENOVACOES"]):
            self.assertEqual(self.client.post(f"/api/emprestimos/{emp_id}/renovar/").status_code, 200)
        self.assertEqual(self.client.post(f"/api/emprestimos/{emp_id}/renovar/").status_code, 400)

    def test_atrasado_aparece_no_filtro_e_bloqueia(self):
        self.ex.situacao = Exemplar.Situacao.EMPRESTADO
        self.ex.save()
        atrasado = Emprestimo.objects.create(
            usuario=self.usuario, exemplar=self.ex,
            data_prevista=timezone.localdate() - timedelta(days=3),
        )
        r = self.client.get("/api/emprestimos/?status=atrasados")
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["dias_atraso"], 3)

        # não renova atrasado
        self.assertEqual(self.client.post(f"/api/emprestimos/{atrasado.id}/renovar/").status_code, 400)
        # não pega outro livro enquanto estiver em atraso
        novo = Exemplar.objects.create(livro=self.livro, tombo="T2")
        self.assertEqual(self.emprestar(exemplar=novo).status_code, 400)

    def test_painel(self):
        self.emprestar()
        r = self.client.get("/api/painel/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["emprestimos_ativos"], 1)
        self.assertEqual(r.data["atrasados"], 0)