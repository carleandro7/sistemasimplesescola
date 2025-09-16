from django.http import HttpResponse
from xhtml2pdf import pisa


from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Aluno, Escola
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required



@login_required
def lista_alunos(request):
    """
    Exibe a lista de alunos cadastrados, com busca por nome ou matrícula e paginação.
    """
    q = request.GET.get('q', '').strip()
    alunos = Aluno.objects.select_related('escola').all()
    if q:
        alunos = alunos.filter(Q(nome__icontains=q) | Q(matricula__icontains=q))

    paginator = Paginator(alunos, 10)  # 10 alunos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'alunos/lista.html', {'alunos': page_obj, 'page_obj': page_obj})

@login_required
def cadastrar_aluno(request):
    """
    Cadastra um novo aluno e cria um usuário vinculado para autenticação.
    """
    escolas = Escola.objects.all()
    erros = {}
    val = {}
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento_str = request.POST.get('data_nascimento', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        escola_id = request.POST.get('escola', '').strip()
        senha = request.POST.get('senha', '').strip()

        val = {
            'nome': nome,
            'data_nascimento': data_nascimento_str,
            'matricula': matricula,
            'email': email,
            'telefone': telefone,
            'escola_id': escola_id,
        }

        # Validação dos campos obrigatórios
        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not data_nascimento_str:
            erros['data_nascimento'] = 'Data de nascimento é obrigatória.'
        if not matricula:
            erros['matricula'] = 'Matrícula é obrigatória.'
        if not email:
            erros['email'] = 'E-mail é obrigatório.'
        if not escola_id:
            erros['escola'] = 'Selecione uma escola.'
        if not senha:
            erros['senha'] = 'Senha é obrigatória.'

        # Validação do formato da data
        data_nascimento = None
        if data_nascimento_str:
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
            except ValueError:
                erros['data_nascimento'] = 'Data de nascimento inválida (use AAAA-MM-DD).'


        # Unicidade para aluno
        if matricula and Aluno.objects.filter(matricula=matricula).exists():
            erros['matricula'] = 'Já existe um aluno com essa matrícula.'
        if email and Aluno.objects.filter(email=email).exists():
            erros['email'] = 'Já existe um aluno com esse e-mail.'
        # Unicidade para usuário
        if matricula and User.objects.filter(username=matricula).exists():
            erros['matricula'] = 'Já existe um usuário com essa matrícula.'

        # Escola
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(id=escola_id)
            except Escola.DoesNotExist:
                erros['escola'] = 'Escola inválida.'


        if not erros:
            try:
            # Inicia uma transação atômica para garantir que usuário e aluno sejam criados juntos
                with transaction.atomic():
                    # Cria o usuário Django vinculado ao aluno
                    user = User.objects.create_user(
                        username=matricula,
                        email=email,
                        password=senha
                    )
                    # Cria o registro do aluno e vincula ao usuário criado
                    aluno = Aluno.objects.create(
                        user=user,
                        nome=nome,
                        data_nascimento=data_nascimento,
                        matricula=matricula,
                        email=email,
                        telefone=telefone,
                        escola=escola
                    )
                # Redireciona para a lista de alunos após cadastro bem-sucedido
                return redirect('lista_alunos')
            except Exception as e:
                erros['matricula'] = 'Erro ao criar usuário/aluno: já existe um usuário ou aluno com essa matrícula.'
        # Se houver erros, re-renderiza com os valores enviados
        return render(request, 'alunos/cadastro.html', {'escolas': escolas, 'erros': erros, 'val': val})

    # GET: renderiza formulário vazio
    return render(request, 'alunos/cadastro.html', {'escolas': escolas, 'erros': erros, 'val': val})

       

@login_required
def editar_aluno(request, pk):
    """
    Edita os dados de um aluno e do usuário vinculado.
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    escolas = Escola.objects.all()
    erros = {}
    val = {}

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        dn_str = request.POST.get("data_nascimento", "").strip()
        matricula = request.POST.get("matricula", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        escola_id = request.POST.get("escola", "").strip()
        senha = request.POST.get("senha", "").strip()

        val = {
            "nome": nome,
            "data_nascimento": dn_str,
            "matricula": matricula,
            "email": email,
            "telefone": telefone,
            "escola_id": escola_id,
        }

        # Validação dos campos obrigatórios
        if not nome:
            erros["nome"] = "Nome é obrigatório."
        if not dn_str:
            erros["data_nascimento"] = "Data de nascimento é obrigatória."
        if not matricula:
            erros["matricula"] = "Matrícula é obrigatória."
        if not email:
            erros["email"] = "E-mail é obrigatório."
        if not escola_id:
            erros["escola"] = "Selecione uma escola."

        # Validação do formato da data
        data_nascimento = None
        if dn_str:
            try:
                data_nascimento = datetime.strptime(dn_str, "%Y-%m-%d").date()
            except ValueError:
                erros["data_nascimento"] = "Data de nascimento inválida (use AAAA-MM-DD)."

        # Unicidade para aluno (ignorando o próprio)
        if matricula and Aluno.objects.exclude(pk=aluno.pk).filter(matricula=matricula).exists():
            erros["matricula"] = "Já existe um aluno com essa matrícula."
        if email and Aluno.objects.exclude(pk=aluno.pk).filter(email=email).exists():
            erros["email"] = "Já existe um aluno com esse e-mail."
        # Unicidade para usuário (ignorando o próprio)
        if matricula and aluno.user.username != matricula and User.objects.exclude(pk=aluno.user.pk).filter(username=matricula).exists():
            erros["matricula"] = "Já existe um usuário com essa matrícula."

        # Escola
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(pk=escola_id)
            except Escola.DoesNotExist:
                erros["escola"] = "Escola inválida."

        if not erros:
            try:
                with transaction.atomic():
                    # Só altera o usuário se algum dado do aluno mudou
                    user = aluno.user
                    user_changed = False
                    if aluno.matricula != matricula:
                        user.username = matricula
                        user_changed = True
                    if aluno.email != email:
                        user.email = email
                        user_changed = True
                    if senha:
                        user.set_password(senha)
                        user_changed = True
                    if user_changed:
                        user.save()

                    # Atualiza os dados do aluno
                    aluno.nome = nome
                    aluno.data_nascimento = data_nascimento
                    aluno.matricula = matricula
                    aluno.email = email
                    aluno.telefone = telefone
                    aluno.escola = escola
                    aluno.save()
                return redirect("lista_alunos")
            except Exception as e:
                erros["matricula"] = "Erro ao atualizar usuário/aluno: já existe um usuário ou aluno com essa matrícula."
        # Se houver erros, re-renderiza com os valores enviados
        contexto = {
            "aluno": aluno,
            "escolas": escolas,
            "erros": erros,
            "val": val,
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

@login_required
def excluir_aluno(request, pk):
    """
    Exclui um aluno do sistema via POST.
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == "POST":
        aluno.delete()
    return redirect("lista_alunos")


@login_required
def lista_escolas(request):
    """
    Exibe a lista de escolas cadastradas.
    """
    escolas = Escola.objects.all()
    return render(request, 'escolas/lista.html', {'escolas': escolas})

@login_required
def cadastrar_escola(request):
    """
    Cadastra uma nova escola.
    """
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
    """
    Edita os dados de uma escola.
    """
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
    """
    Exclui uma escola do sistema via POST.
    """
    escola = get_object_or_404(Escola, pk=pk)
    if request.method == 'POST':
        escola.delete()
    return redirect('lista_escolas')

@login_required
def area_aluno(request):
    """
    Exibe a área do aluno logado.
    """
    # Se quiser pegar o Aluno vinculado:
    # aluno = request.user.aluno  (por causa do related_name='aluno')
    return render(request, "alunos/area_aluno.html")

def login_aluno(request):
    """
    Autentica o aluno usando matrícula e senha.
    """
    if request.method == "POST":
        matricula = request.POST.get("matricula")
        senha = request.POST.get("senha")
        user = authenticate(request, username=matricula, password=senha)
        if user is not None:
            login(request, user)
            return redirect("area_aluno")  # página inicial do aluno (você define)
        else:
            return render(request, "alunos/login.html", {"erro": "Credenciais inválidas."})
    return render(request, "alunos/login.html")

def logout_aluno(request):
    """
    Realiza logout do aluno.
    """
    logout(request)
    return redirect("login_aluno")

# Login
def login_view(request):
    """
    Autentica usuário padrão Django (username/senha).
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('lista_alunos')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})
    return render(request, 'login.html')

# Logout
def logout_view(request):
    """
    Realiza logout do usuário padrão Django.
    """
    logout(request)
    return redirect('login')


@login_required
def alunos_pdf(request):
    """
    Gera e retorna um PDF com os dados de todos os alunos usando um template HTML.
    """
    # Busca todos os alunos, incluindo o nome da escola
    alunos = Aluno.objects.select_related('escola').all()

    # Caminho do template HTML que será usado para gerar o PDF
    template_path = 'alunos/pdf.html'
    context = {'alunos': alunos}

    # Renderiza o template HTML com os dados dos alunos
    html = render(request, template_path, context).content.decode('utf-8')

    # Cria a resposta HTTP para download do PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="alunos.pdf"'

    # Converte o HTML renderizado em PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Se houver erro na geração do PDF, retorna mensagem de erro
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    # Retorna o PDF gerado para download
    return response