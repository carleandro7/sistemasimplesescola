
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required
from escola.models import Aluno, Escola
from datetime import datetime
from django.http import HttpResponse
from xhtml2pdf import pisa

@login_required
def lista_alunos(request):
    q = request.GET.get('q', '').strip()
    alunos = Aluno.objects.select_related('escola').all()
    if q:
        alunos = alunos.filter(Q(nome__icontains=q) | Q(matricula__icontains=q))
    paginator = Paginator(alunos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'alunos/lista.html', {'alunos': page_obj, 'page_obj': page_obj})

@login_required
def cadastrar_aluno(request):
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
        data_nascimento = None
        if data_nascimento_str:
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
            except ValueError:
                erros['data_nascimento'] = 'Data de nascimento inválida (use AAAA-MM-DD).'
        if matricula and Aluno.objects.filter(matricula=matricula).exists():
            erros['matricula'] = 'Já existe um aluno com essa matrícula.'
        if email and Aluno.objects.filter(email=email).exists():
            erros['email'] = 'Já existe um aluno com esse e-mail.'
        if matricula and User.objects.filter(username=matricula).exists():
            erros['matricula'] = 'Já existe um usuário com essa matrícula.'
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(id=escola_id)
            except Escola.DoesNotExist:
                erros['escola'] = 'Escola inválida.'
        if not erros:
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=matricula,
                        email=email,
                        password=senha
                    )
                    aluno = Aluno.objects.create(
                        user=user,
                        nome=nome,
                        data_nascimento=data_nascimento,
                        matricula=matricula,
                        email=email,
                        telefone=telefone,
                        escola=escola
                    )
                return redirect('lista_alunos')
            except Exception as e:
                erros['matricula'] = 'Erro ao criar usuário/aluno: já existe um usuário ou aluno com essa matrícula.'
        return render(request, 'alunos/cadastro.html', {'escolas': escolas, 'erros': erros, 'val': val})
    return render(request, 'alunos/cadastro.html', {'escolas': escolas, 'erros': erros, 'val': val})

@login_required
def editar_aluno(request, pk):
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
        data_nascimento = None
        if dn_str:
            try:
                data_nascimento = datetime.strptime(dn_str, "%Y-%m-%d").date()
            except ValueError:
                erros["data_nascimento"] = "Data de nascimento inválida (use AAAA-MM-DD)."
        if matricula and Aluno.objects.exclude(pk=aluno.pk).filter(matricula=matricula).exists():
            erros["matricula"] = "Já existe um aluno com essa matrícula."
        if email and Aluno.objects.exclude(pk=aluno.pk).filter(email=email).exists():
            erros["email"] = "Já existe um aluno com esse e-mail."
        if matricula and aluno.user.username != matricula and User.objects.exclude(pk=aluno.user.pk).filter(username=matricula).exists():
            erros["matricula"] = "Já existe um usuário com essa matrícula."
        escola = None
        if escola_id:
            try:
                escola = Escola.objects.get(pk=escola_id)
            except Escola.DoesNotExist:
                erros["escola"] = "Escola inválida."
        if not erros:
            try:
                with transaction.atomic():
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
        contexto = {
            "aluno": aluno,
            "escolas": escolas,
            "erros": erros,
            "val": val,
        }
        return render(request, "alunos/editar.html", contexto)
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
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == "POST":
        aluno.delete()
    return redirect("lista_alunos")

@login_required
def alunos_pdf(request):
    alunos = Aluno.objects.select_related('escola').all()
    template_path = 'alunos/pdf.html'
    context = {'alunos': alunos}
    html = render(request, template_path, context).content.decode('utf-8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="alunos.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response
