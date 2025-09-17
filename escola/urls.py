from django.urls import path
from views import escola_views, login_views, aluno_views

urlpatterns = [
    path('alunos/', aluno_views.lista_alunos, name='lista_alunos'),
    path('alunos/pdf/', aluno_views.alunos_pdf, name='alunos_pdf'),
    path('alunos/cadastrar/', aluno_views.cadastrar_aluno, name='cadastrar_aluno'),
    path('alunos/<int:pk>/editar/', aluno_views.editar_aluno, name='editar_aluno'),
    path('alunos/<int:pk>/excluir/', aluno_views.excluir_aluno, name='excluir_aluno'),

    # Rotas Escola
    path('escolas/', escola_views.lista_escolas, name='lista_escolas'),
    path('escolas/cadastrar/', escola_views.cadastrar_escola, name='cadastrar_escola'),
    path('escolas/<int:pk>/editar/', escola_views.editar_escola, name='editar_escola'),
    path('escolas/<int:pk>/excluir/', escola_views.excluir_escola, name='excluir_escola'),

    # Autenticação
    path('login/', login_views.login_view, name='login'),
    path('logout/', login_views.logout_view, name='logout'),
    path('', aluno_views.area_aluno, name='area_aluno'),
]
