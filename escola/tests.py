
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Aluno, Escola
from datetime import date

class ViewsTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.escola = Escola.objects.create(nome="Escola Teste", endereco="Rua 1", cidade="Cidade", estado="UF", telefone="123456")
		self.user = User.objects.create_user(username="123", password="senha123", email="teste@email.com")
		self.aluno = Aluno.objects.create(user=self.user, nome="Aluno Teste", data_nascimento=date(2000,1,1), matricula="123", email="teste@email.com", telefone="99999", escola=self.escola)

	def test_lista_alunos_login_required(self):
		response = self.client.get(reverse('lista_alunos'))
		self.assertEqual(response.status_code, 302)  # Redireciona para login

	def test_lista_alunos_authenticated(self):
		self.client.login(username="123", password="senha123")
		response = self.client.get(reverse('lista_alunos'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aluno Teste")

	def test_cadastrar_aluno_get(self):
		self.client.login(username="123", password="senha123")
		response = self.client.get(reverse('cadastrar_aluno'))
		self.assertEqual(response.status_code, 200)

	def test_cadastrar_aluno_post(self):
		self.client.login(username="123", password="senha123")
		data = {
			'nome': 'Novo Aluno',
			'data_nascimento': '2001-01-01',
			'matricula': '456',
			'email': 'novo@email.com',
			'telefone': '88888',
			'escola': str(self.escola.id),
			'senha': 'senha456',
		}
		response = self.client.post(reverse('cadastrar_aluno'), data)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(Aluno.objects.filter(matricula='456').exists())

	def test_editar_aluno(self):
		self.client.login(username="123", password="senha123")
		url = reverse('editar_aluno', args=[self.aluno.pk])
		data = {
			'nome': 'Aluno Editado',
			'data_nascimento': '2000-01-01',
			'matricula': '123',
			'email': 'teste@email.com',
			'telefone': '99999',
			'escola': str(self.escola.id),
			'senha': '',
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)
		self.aluno.refresh_from_db()
		self.assertEqual(self.aluno.nome, 'Aluno Editado')

	def test_excluir_aluno(self):
		self.client.login(username="123", password="senha123")
		url = reverse('excluir_aluno', args=[self.aluno.pk])
		response = self.client.post(url)
		self.assertEqual(response.status_code, 302)
		self.assertFalse(Aluno.objects.filter(pk=self.aluno.pk).exists())


	def test_login_aluno(self):
		# Testa login do aluno usando matrícula como username e senha
		response = self.client.post(reverse('login'), {'username': '123', 'password': 'senha123'})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('area_aluno'))

	def test_login_padrao(self):
		# Testa login padrão Django usando username e senha
		response = self.client.post(reverse('login'), {'username': '123', 'password': 'senha123'})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('area_aluno'))

	def test_logout(self):
		self.client.login(username="123", password="senha123")
		response = self.client.get(reverse('logout'))
		self.assertEqual(response.status_code, 302)

	def test_area_aluno_requires_login(self):
		response = self.client.get(reverse('area_aluno'))
		self.assertEqual(response.status_code, 302)

	def test_area_aluno_authenticated(self):
		self.client.login(username="123", password="senha123")
		response = self.client.get(reverse('area_aluno'))
		self.assertEqual(response.status_code, 200)
