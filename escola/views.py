from django.shortcuts import render, redirect
from .models import Aluno, Escola

def lista_alunos(request):
    alunos = Aluno.objects.select_related('escola').all()
    return render(request, 'alunos/lista.html', {'alunos': alunos})

def cadastrar_aluno(request):
    escolas = Escola.objects.all()
    if request.method == 'POST':
        nome = request.POST['nome']
        data_nascimento = request.POST['data_nascimento']
        matricula = request.POST['matricula']
        email = request.POST['email']
        telefone = request.POST['telefone']
        escola_id = request.POST['escola']

        escola = Escola.objects.get(id=escola_id)
        Aluno.objects.create(
            nome=nome,
            data_nascimento=data_nascimento,
            matricula=matricula,
            email=email,
            telefone=telefone,
            escola=escola
        )
        return redirect('lista_alunos')
    
    return render(request, 'alunos/cadastro.html', {'escolas': escolas})
