from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from escola.models import Escola

@login_required
def lista_escolas(request):
    escolas = Escola.objects.all()
    return render(request, 'escolas/lista.html', {'escolas': escolas})

@login_required
def cadastrar_escola(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        endereco = request.POST['endereco']
        cidade = request.POST['cidade']
        estado = request.POST['estado']
        telefone = request.POST['telefone']
        Escola.objects.create(
            nome=nome,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            telefone=telefone
        )
        return redirect('lista_escolas')
    return render(request, 'escolas/cadastro.html')

@login_required
def editar_escola(request, pk):
    escola = get_object_or_404(Escola, pk=pk)
    if request.method == 'POST':
        escola.nome = request.POST['nome']
        escola.endereco = request.POST['endereco']
        escola.cidade = request.POST['cidade']
        escola.estado = request.POST['estado']
        escola.telefone = request.POST['telefone']
        escola.save()
        return redirect('lista_escolas')
    return render(request, 'escolas/editar.html', {'escola': escola})

@login_required
def excluir_escola(request, pk):
    escola = get_object_or_404(Escola, pk=pk)
    if request.method == 'POST':
        escola.delete()
    return redirect('lista_escolas')
