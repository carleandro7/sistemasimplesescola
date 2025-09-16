# Sistema Simples Escola

Este projeto é um sistema simples de gerenciamento escolar desenvolvido em Python utilizando o framework Django.

## Funcionalidades
- Cadastro, edição e listagem de alunos
- Cadastro, edição e listagem de escolas
- Área do aluno
- Geração de PDF de alunos
- Autenticação de usuários
- Paginação de listas

## Estrutura do Projeto
- `core/`: Configurações principais do projeto Django
- `escola/`: Aplicação principal com modelos, views, templates e migrações
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `templates/`: Templates HTML para as páginas do sistema

## Requisitos
- Python 3.10+
- Django 4.x

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/carleandro7/sistemasimplesescola.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
4. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

## Uso
Acesse `http://localhost:8000/` no navegador para utilizar o sistema.

## Licença
Este projeto está sob a licença MIT.
