from django.urls import path
from . import views

urlpatterns = [
    path('alunos/', views.lista_alunos, name='lista_alunos'),
    path('alunos/cadastrar/', views.cadastrar_aluno, name='cadastrar_aluno'),
    path('alunos/<int:pk>/editar/', views.editar_aluno, name='editar_aluno'),
    path('alunos/<int:pk>/excluir/', views.excluir_aluno, name='excluir_aluno'),

    # Rotas Escola
    path('escolas/', views.lista_escolas, name='lista_escolas'),
    path('escolas/cadastrar/', views.cadastrar_escola, name='cadastrar_escola'),
    path('escolas/<int:pk>/editar/', views.editar_escola, name='editar_escola'),
    path('escolas/<int:pk>/excluir/', views.excluir_escola, name='excluir_escola'),
]
