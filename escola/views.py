from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
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

def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    escolas = Escola.objects.all()
    erros = {}

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        dn_str = request.POST.get("data_nascimento", "").strip()
        matricula = request.POST.get("matricula", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        escola_id = request.POST.get("escola", "").strip()

        # Campos obrigatórios mínimos
        if not nome:
            erros["nome"] = "Nome é obrigatório."
        if not matricula:
            erros["matricula"] = "Matrícula é obrigatória."
        if not email:
            erros["email"] = "E-mail é obrigatório."
        if not escola_id:
            erros["escola"] = "Selecione uma escola."

        # Unicidade (ignorando o próprio aluno)
        if matricula and Aluno.objects.exclude(pk=aluno.pk).filter(matricula=matricula).exists():
            erros["matricula"] = "Já existe um aluno com essa matrícula."
        if email and Aluno.objects.exclude(pk=aluno.pk).filter(email=email).exists():
            erros["email"] = "Já existe um aluno com esse e-mail."

        # Parse da data opcional
        data_nascimento = None
        if dn_str:
            try:
                data_nascimento = datetime.strptime(dn_str, "%Y-%m-%d").date()
            except ValueError:
                erros["data_nascimento"] = "Data de nascimento inválida (use AAAA-MM-DD)."

        # Escola
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(pk=escola_id)
            except Escola.DoesNotExist:
                erros["escola"] = "Escola inválida."

        if not erros:
            aluno.nome = nome
            aluno.data_nascimento = data_nascimento  # opcional
            aluno.matricula = matricula
            aluno.email = email
            aluno.telefone = telefone  # opcional (pode ser vazio)
            aluno.escola = escola
            aluno.save()
            return redirect("lista_alunos")

        # Se houver erros, re-renderiza com os valores enviados
        contexto = {
            "aluno": aluno,
            "escolas": escolas,
            "erros": erros,
            "val": {
                "nome": nome,
                "data_nascimento": dn_str,
                "matricula": matricula,
                "email": email,
                "telefone": telefone,
                "escola_id": escola_id,
            },
        }
        return render(request, "alunos/editar.html", contexto)

    # GET: pré-preenche com os dados do aluno
    contexto = {
        "aluno": aluno,
        "escolas": escolas,
        "erros": {},
        "val": {
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento.strftime("%Y-%m-%d") if aluno.data_nascimento else "",
            "matricula": aluno.matricula,
            "email": aluno.email,
            "telefone": aluno.telefone or "",
            "escola_id": str(aluno.escola_id),
        },
    }
    return render(request, "alunos/editar.html", contexto)


def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == "POST":
        aluno.delete()
    return redirect("lista_alunos")


# CRUD Escola
def lista_escolas(request):
    escolas = Escola.objects.all()
    return render(request, 'escolas/lista.html', {'escolas': escolas})

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

def excluir_escola(request, pk):
    escola = get_object_or_404(Escola, pk=pk)
    if request.method == 'POST':
        escola.delete()
    return redirect('lista_escolas')

