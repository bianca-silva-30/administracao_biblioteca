from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Exemplar, Livro


class AcervoAPITests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(
            get_user_model().objects.create_user(username="bib01", password="senha-forte-123")
        )

    def test_dois_livros_sem_isbn(self):
        for titulo in ("Livro A", "Livro B"):
            r = self.client.post("/api/livros/", {"titulo": titulo, "isbn": ""})
            self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(Livro.objects.filter(isbn__isnull=True).count(), 2)

    def test_contagem_de_exemplares(self):
        livro = Livro.objects.create(titulo="Livro A")
        Exemplar.objects.create(livro=livro, tombo="T1")
        Exemplar.objects.create(livro=livro, tombo="T2", situacao=Exemplar.Situacao.PERDIDO)
        r = self.client.get("/api/livros/")
        item = r.data["results"][0]
        self.assertEqual(item["total_exemplares"], 2)
        self.assertEqual(item["exemplares_disponiveis"], 1)

    def test_nao_define_emprestado_manualmente(self):
        livro = Livro.objects.create(titulo="Livro A")
        r = self.client.post("/api/exemplares/", {
            "livro": livro.id, "tombo": "T1", "situacao": "emprestado",
        })
        self.assertEqual(r.status_code, 400)

        def test_cria_livro_com_exemplares_e_nomes(self):
            r = self.client.post("/api/livros/", {
                "titulo": "Dom Casmurro", "autor_texto": "Machado de Assis",
                "categoria_texto": "Literatura", "quantidade_exemplares": 3,
            })
            self.assertEqual(r.status_code, 201, r.data)
            self.assertEqual(r.data["total_exemplares"], 3)
            self.assertEqual(r.data["autores_nomes"], ["Machado de Assis"])
            self.assertEqual(r.data["categoria_nome"], "Literatura")