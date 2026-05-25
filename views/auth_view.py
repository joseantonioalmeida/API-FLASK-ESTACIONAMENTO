from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request, session
from flask_mail import Mail, Message
import random
import string
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from utils import login_required


load_dotenv()


# Configuração global para armazenar códigos de recuperação de senha
# Formato: {email: {"codigo": "123456", "data_expiracao": datetime, "tentativas": 0}}
codigos_recuperacao = {}


@app.route('/auth/register/', methods=['POST'])
def register():
    """
    Rota para criar uma nova conta de usuário.
    
    JSON esperado:
    {
        "username": "usuario_exemplo",
        "email": "usuario@email.com",
        "password": "senha_segura",
        "first_name": "Nome",
        "last_name": "Sobrenome"
    }
    """
    try:
        dados_recebidos = request.get_json()
        
        username = dados_recebidos.get("username")
        email = dados_recebidos.get("email")
        password = dados_recebidos.get("password")
        first_name = dados_recebidos.get("first_name", "")
        last_name = dados_recebidos.get("last_name", "")
        
        # Validação de campos obrigatórios
        if not username or not email or not password:
            return make_response(
                jsonify(mensagem="Os campos 'username', 'email' e 'password' são obrigatórios."),
                400
            )
        
        # Validação básica de email
        if "@" not in email or "." not in email.split("@")[1]:
            return make_response(
                jsonify(mensagem="Email inválido."),
                400
            )
        
        banco = connect_db()
        cursor = banco.cursor()
        
        # Verifica se o username ou email já existem
        sql_check_username = "SELECT id FROM auth_user WHERE username = %s"
        cursor.execute(sql_check_username, (username,))
        if cursor.fetchone():
            banco.close()
            return make_response(
                jsonify(mensagem="Este username já está cadastrado."),
                400
            )
        
        sql_check_email = "SELECT id FROM auth_user WHERE email = %s"
        cursor.execute(sql_check_email, (email,))
        if cursor.fetchone():
            banco.close()
            return make_response(
                jsonify(mensagem="Este email já está cadastrado."),
                400
            )
        
        # Insere o novo usuário
        sql = '''INSERT INTO auth_user (username, email, password, first_name, last_name, is_active) 
                 VALUES (%s, %s, %s, %s, %s, 1)'''
        cursor.execute(sql, (username, email, password, first_name, last_name))
        banco.commit()
        
        id_criado = cursor.lastrowid
        
        # Busca o usuário recém-criado
        sql = '''SELECT id, username, email, first_name, last_name, is_active, date_joined 
                 FROM auth_user WHERE id = %s'''
        cursor.execute(sql, (id_criado,))
        usuario = cursor.fetchone()
        banco.close()
        
        usuario_json = {
            "id": usuario[0], #type:ignore
            "username": usuario[1], #type:ignore
            "email": usuario[2], #type:ignore
            "first_name": usuario[3], #type:ignore
            "last_name": usuario[4], #type:ignore
            "is_active": bool(usuario[5]), #type:ignore
            "date_joined": str(usuario[6]) #type:ignore
        }
        
        return make_response(
            jsonify(
                mensagem="Conta criada com sucesso. Bem-vindo!",
                dados=usuario_json
            ),
            201
        )
        
    except Exception as e:
        return make_response(
            jsonify(mensagem="Erro interno ao criar conta.", erro=str(e)),
            500
        )


@app.route('/auth/login/', methods=['POST'])
def login():
    """
    Rota para fazer login na aplicação.
    
    JSON esperado:
    {
        "email": "usuario@email.com",
        "password": "senha"
    }
    """
    try:
        dados_recebidos = request.get_json()
        
        email = dados_recebidos.get("email")
        password = dados_recebidos.get("password")
        
        # Validação de campos obrigatórios
        if not email or not password:
            return make_response(
                jsonify(mensagem="Email e senha são obrigatórios."),
                400
            )
        
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = '''SELECT id, username, email, password, is_active, first_name, last_name 
                 FROM auth_user WHERE email = %s'''
        cursor.execute(sql, (email,))
        usuario = cursor.fetchone()
        banco.close()
        
        # Validação de credenciais
        if not usuario:
            return make_response(
                jsonify(mensagem="Email ou senha incorretos."),
                401
            )
        
        # Verifica se a senha está correta (comparação simples - em produção usar hash)
        if usuario[3] != password:
            return make_response(
                jsonify(mensagem="Email ou senha incorretos."),
                401
            )
        
        # Verifica se a conta está ativa
        if not bool(usuario[4]):
            return make_response(
                jsonify(mensagem="Esta conta foi desativada."),
                403
            )
        
        # Cria a sessão
        session['usuario_id'] = usuario[0]
        session['usuario_email'] = usuario[2]
        
        usuario_json = {
            "id": usuario[0],
            "username": usuario[1],
            "email": usuario[2],
            "first_name": usuario[5],
            "last_name": usuario[6],
            "mensagem": "Login realizado com sucesso!"
        }
        
        return make_response(
            jsonify(usuario_json),
            200
        )
        
    except Exception as e:
        return make_response(
            jsonify(mensagem="Erro interno ao fazer login.", erro=str(e)),
            500
        )


@app.route('/auth/logout/', methods=['POST'])
@login_required
def logout():
    """
    Rota para fazer logout da aplicação.
    """
    try:
        # Remove dados da sessão
        session.pop('usuario_id', None)
        session.pop('usuario_email', None)
        
        return make_response(
            jsonify(mensagem="Logout realizado com sucesso."),
            200
        )
        
    except Exception as e:
        return make_response(
            jsonify(mensagem="Erro ao fazer logout.", erro=str(e)),
            500
        )


@app.route('/auth/password-recovery/', methods=['POST'])
@login_required
def password_recovery():
    """
    Rota para recuperar senha enviando um código por email.
    
    JSON esperado:
    {
        "email": "usuario@email.com"
    }
    """
    try:
        dados_recebidos = request.get_json()
        email = dados_recebidos.get("email")
        
        if not email:
            return make_response(
                jsonify(mensagem="Email é obrigatório."),
                400
            )
        
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = '''SELECT id, username, email, first_name FROM auth_user WHERE email = %s'''
        cursor.execute(sql, (email,))
        usuario = cursor.fetchone()
        banco.close()
        
        if not usuario:
            return make_response(
                jsonify(mensagem="Email não encontrado no sistema."),
                404
            )
        
        # Gera um código de recuperação com 6 dígitos
        codigo_recuperacao = ''.join(random.choices(string.digits, k=6))
        
        # Armazena o código com data de expiração (válido por 15 minutos)
        codigos_recuperacao[email] = {
            "codigo": codigo_recuperacao,
            "data_expiracao": datetime.now() + timedelta(minutes=15),
            "tentativas": 0
        }
        
        try:
            # Configuração do Flask-Mail (variáveis de ambiente)
            app.config['MAIL_SERVER'] = os.getenv('mail_server', 'smtp.gmail.com')
            app.config['MAIL_PORT'] = int(os.getenv('mail_port', 587))
            app.config['MAIL_USE_TLS'] = os.getenv('mail_use_tls', 'True') == 'True'
            app.config['MAIL_USERNAME'] = os.getenv('mail_username', 'change-me')
            app.config['MAIL_PASSWORD'] = os.getenv('mail_password', 'change-me')
            
            mail = Mail(app)
            
            msg = Message(
                "Código de Recuperação de Senha",
                sender=os.getenv('mail_username', 'change-me'),
                recipients=[email]
            )
            msg.body = f"""Olá {usuario[2]},

Você solicitou a recuperação de senha. Use o código abaixo para resetar sua senha.
Este código é válido por 15 minutos.

Código: {codigo_recuperacao}

Se você não solicitou essa recuperação, ignore este email.

Atenciosamente,
Sistema de Estacionamento"""
            
            mail.send(msg)
            
        except Exception as e:
            # Se o email não conseguir ser enviado, remove o código armazenado
            codigos_recuperacao.pop(email, None)
            return make_response(
                jsonify(mensagem="Erro ao enviar email. Tente novamente mais tarde.", erro=str(e)),
                500
            )
        
        return make_response(
            jsonify(
                mensagem="Código de recuperação enviado com sucesso para seu email.",
                usuario={
                    "id": usuario[0],
                    "username": usuario[1],
                    "email": usuario[3]
                }
            ),
            200
        )
        
    except Exception as e:
        return make_response(
            jsonify(mensagem="Erro interno ao processar recuperação de senha.", erro=str(e)),
            500
        )


@app.route('/auth/password-reset/', methods=['PUT'])
@login_required
def password_reset():
    """
    Rota para resetar a senha usando o código de recuperação.
    
    JSON esperado:
    {
        "email": "usuario@email.com",
        "codigo_recuperacao": "123456",
        "nova_senha": "nova_senha_segura"
    }
    """
    try:
        dados_recebidos = request.get_json()
        
        email = dados_recebidos.get("email")
        codigo_recebido = dados_recebidos.get("codigo_recuperacao")
        nova_senha = dados_recebidos.get("nova_senha")
        
        # Validação de campos obrigatórios
        if not email or not codigo_recebido or not nova_senha:
            return make_response(
                jsonify(mensagem="Email, código de recuperação e nova senha são obrigatórios."),
                400
            )
        
        # Validação de senha (mínimo 6 caracteres)
        if len(nova_senha) < 6:
            return make_response(
                jsonify(mensagem="A nova senha deve ter no mínimo 6 caracteres."),
                400
            )
        
        # Verifica se existe um código para este email
        if email not in codigos_recuperacao:
            return make_response(
                jsonify(mensagem="Nenhum código de recuperação ativo para este email."),
                400
            )
        
        dados_codigo = codigos_recuperacao[email]
        
        # Verifica se o código expirou
        if datetime.now() > dados_codigo["data_expiracao"]:
            codigos_recuperacao.pop(email, None)
            return make_response(
                jsonify(mensagem="Código de recuperação expirado. Solicite um novo código."),
                400
            )
        
        # Verifica se o código está correto
        if dados_codigo["codigo"] != codigo_recebido:
            dados_codigo["tentativas"] += 1
            
            # Bloqueia após 3 tentativas erradas
            if dados_codigo["tentativas"] >= 3:
                codigos_recuperacao.pop(email, None)
                return make_response(
                    jsonify(mensagem="Máximo de tentativas excedido. Solicite um novo código."),
                    400
                )
            
            return make_response(
                jsonify(mensagem=f"Código incorreto. Tentativas restantes: {3 - dados_codigo['tentativas']}."),
                400
            )
        
        # Atualiza a senha no banco de dados
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = '''UPDATE auth_user SET password = %s WHERE email = %s'''
        cursor.execute(sql, (nova_senha, email))
        banco.commit()
        banco.close()
        
        # Remove o código de recuperação após uso bem-sucedido
        codigos_recuperacao.pop(email, None)
        
        return make_response(
            jsonify(mensagem="Senha atualizada com sucesso! Você pode fazer login agora."),
            200
        )
        
    except Exception as e:
        return make_response(
            jsonify(mensagem="Erro interno ao atualizar senha.", erro=str(e)),
            500
        )
