from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from utils import login_required


@app.route('/users/', methods=['GET'])
@login_required
def get_users():
    try:
        banco = connect_db()
        cursor = banco.cursor()

        sql = 'SELECT id, username, email, is_active FROM auth_user;'
        cursor.execute(sql)
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_users_json = [
            {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "is_active": bool(user[3])  # Converte tinyint(1) para True/False
            }
            for user in resultado_fetchall
        ]

        # Ordena pelo ID de forma decrescente (mais recentes primeiro)
        lista_users_json_ordenada = sorted(
            lista_users_json,
            key=lambda x: x['id'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de Usuários.',
                total=len(lista_users_json_ordenada),
                dados=lista_users_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao listar usuários.", erro=str(e)), 500)


@app.route('/users/<int:id>/', methods=['GET'])
@login_required
def get_user_detail(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        # Mapeamento completo com base em todas as colunas da imagem
        sql = '''SELECT id, password, last_login, is_superuser, username, 
                        first_name, last_name, email, is_staff, is_active, date_joined 
                 FROM auth_user WHERE id = %s;'''
        cursor.execute(sql, (id,))
        user = cursor.fetchone()
        banco.close()

        if not user:
            return make_response(jsonify(mensagem="Usuário não encontrado."), 404)
        
        user_json = {
            "id": user[0],
            "password": user[1],
            "last_login": str(user[2]) if user[2] else None, # Trata datetime nulo
            "is_superuser": bool(user[3]),
            "username": user[4],
            "first_name": user[5],
            "last_name": user[6],
            "email": user[7],
            "is_staff": bool(user[8]),
            "is_active": bool(user[9]),
            "date_joined": str(user[10])
        }
        return make_response(jsonify(mensagem="Detalhes do Usuário.", dados=user_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar usuário.", erro=str(e)), 500)


@app.route('/users/', methods=['POST'])
@login_required
def create_user():
    try:
        dados_recebidos = request.get_json()
        
        username = dados_recebidos.get("username")
        password = dados_recebidos.get("password")
        email = dados_recebidos.get("email", "")
        first_name = dados_recebidos.get("first_name", "")
        last_name = dados_recebidos.get("last_name", "")
        
        # Pega as flags booleanas (padrão baseado nos Defaults se não enviados)
        is_superuser = dados_recebidos.get("is_superuser", 0)
        is_staff = dados_recebidos.get("is_staff", 0)
        is_active = dados_recebidos.get("is_active", 1)

        if not username or not password:
            return make_response(jsonify(mensagem="Username e password são obrigatórios."), 400)

        banco = connect_db()
        cursor = banco.cursor()
        
        # O campo date_joined possui DEFAULT_GENERATED, então o MySQL preenche sozinho se omitido
        sql = '''INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(sql, (password, is_superuser, username, first_name, last_name, email, is_staff, is_active))
        banco.commit()

        id_criado = cursor.lastrowid
        
        # Busca o usuário recém-criado para retornar
        sql = '''SELECT id, password, last_login, is_superuser, username, 
                        first_name, last_name, email, is_staff, is_active, date_joined 
                 FROM auth_user WHERE id = %s;'''
        cursor.execute(sql, (id_criado,))
        u = cursor.fetchone()
        banco.close()

        user_json = {
            "id": u[0], "password": u[1], "last_login": str(u[2]) if u[2] else None, #type:ignore
            "is_superuser": bool(u[3]), "username": u[4], "first_name": u[5], #type:ignore
            "last_name": u[6], "email": u[7], "is_staff": bool(u[8]), #type:ignore
            "is_active": bool(u[9]), "date_joined": str(u[10]) #type:ignore
        }
        return make_response(jsonify(mensagem="Usuário criado com sucesso.", dados=user_json), 201)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar usuário.", erro=str(e)), 500)


@app.route('/users/<int:id>/', methods=['PUT'])
@login_required
def put_user(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        # Validação Prévia se o registro existe
        sql = 'SELECT password, is_superuser, username, first_name, last_name, email, is_staff, is_active FROM auth_user WHERE id = %s;'
        cursor.execute(sql, (id,))
        user_atual = cursor.fetchone()
        
        if not user_atual:
            banco.close()
            return make_response(jsonify(mensagem='Usuário não encontrado para atualização.'), 404)

        dados_recebidos = request.get_json()
        
        # Mantém o valor atual do banco se o campo não for enviado no JSON (.get parcial)
        password = dados_recebidos.get('password', user_atual[0])
        is_superuser = dados_recebidos.get('is_superuser', user_atual[1])
        username = dados_recebidos.get('username', user_atual[2])
        first_name = dados_recebidos.get('first_name', user_atual[3])
        last_name = dados_recebidos.get('last_name', user_atual[4])
        email = dados_recebidos.get('email', user_atual[5])
        is_staff = dados_recebidos.get('is_staff', user_atual[6])
        is_active = dados_recebidos.get('is_active', user_atual[7])

        sql = '''UPDATE auth_user 
                 SET password=%s, is_superuser=%s, username=%s, first_name=%s, last_name=%s, email=%s, is_staff=%s, is_active=%s 
                 WHERE id=%s'''
        cursor.execute(sql, (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, id))
        banco.commit()

        # Busca o usuário atualizado final
        sql = '''SELECT id, password, last_login, is_superuser, username, 
                        first_name, last_name, email, is_staff, is_active, date_joined 
                 FROM auth_user WHERE id = %s;'''
        cursor.execute(sql, (id,))
        u = cursor.fetchone()
        banco.close()
        
        user_json = {
            "id": u[0], "password": u[1], "last_login": str(u[2]) if u[2] else None, #type:ignore
            "is_superuser": bool(u[3]), "username": u[4], "first_name": u[5], #type:ignore
            "last_name": u[6], "email": u[7], "is_staff": bool(u[8]), #type:ignore
            "is_active": bool(u[9]), "date_joined": str(u[10]) #type:ignore
        }
        return make_response(jsonify(mensagem="Usuário atualizado com sucesso.", dados=user_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar usuário.", erro=str(e)), 500)


@app.route('/users/<int:id>/', methods=['DELETE'])
@login_required
def delete_user(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'SELECT id FROM auth_user WHERE id=%s;'
        cursor.execute(sql, (id,))
        user = cursor.fetchone()
        
        if not user:
            banco.close()
            return make_response(jsonify(mensagem='Usuário não encontrado para deletar.'), 404)

        sql = 'DELETE FROM auth_user WHERE id=%s;'
        cursor.execute(sql, (id,))
        banco.commit()
        banco.close()

        return make_response(jsonify(mensagem="Usuário deletado com sucesso."), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar usuário.", erro=str(e)), 500)
