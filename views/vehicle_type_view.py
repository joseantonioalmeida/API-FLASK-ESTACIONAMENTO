from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from utils import login_required


@app.route('/vehicle-types/', methods=['GET'])
@login_required
def get_vehicle_types():
    try:
        banco = connect_db()
        cursor = banco.cursor()
        sql = 'SELECT id, name, description FROM vehicle_type;'
        cursor.execute(sql)
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_types_json = [
            {
                "id": vt[0],
                "name": vt[1],
                "description": vt[2]  # Pode retornar None caso esteja nulo no banco
            }
            for vt in resultado_fetchall
        ]

        lista_types_json_ordenada = sorted(
            lista_types_json,
            key=lambda x: x['id'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de tipos de veículos.',
                total=len(lista_types_json_ordenada),
                dados=lista_types_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao listar tipos de veículos.", erro=str(e)), 500)


@app.route('/vehicle-types/<int:id>/', methods=['GET'])
@login_required
def get_vehicle_type_detail(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        sql = 'SELECT id, name, description FROM vehicle_type WHERE id = %s;'
        cursor.execute(sql, (id,))
        vt = cursor.fetchone()
        banco.close()

        if not vt:
            return make_response(jsonify(mensagem="Tipo de veículo não encontrado."), 404)
        
        type_json = {
            "id": vt[0],
            "name": vt[1],
            "description": vt[2]
        }
        return make_response(jsonify(mensagem="Detalhes do tipo de veículo.", dados=type_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar tipo de veículo.", erro=str(e)), 500)


@app.route('/vehicle-types/', methods=['POST'])
@login_required
def create_vehicle_type():
    try:
        dados_recebidos = request.get_json()
        
        name = dados_recebidos.get("name")
        description = dados_recebidos.get("description", None) # Default None se não enviado

        if not name:
            return make_response(jsonify(mensagem="O campo 'name' é obrigatório."), 400)

        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'INSERT INTO vehicle_type (name, description) VALUES (%s, %s);'
        cursor.execute(sql, (name, description))
        banco.commit()

        id_criado = cursor.lastrowid
        
        # Busca o registro criado para retornar os dados completos
        sql = 'SELECT id, name, description FROM vehicle_type WHERE id = %s;'
        cursor.execute(sql, (id_criado,))
        vt = cursor.fetchone()
        banco.close()

        type_json = {
            "id": vt[0], #type:ignore
            "name": vt[1], #type:ignore
            "description": vt[2] #type:ignore
        }
        return make_response(jsonify(mensagem="Tipo de veículo criado com sucesso.", dados=type_json), 201)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar tipo de veículo.", erro=str(e)), 500)


@app.route('/vehicle-types/<int:id>/', methods=['PUT'])
@login_required
def put_vehicle_type(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        # Validação prévia de existência
        sql = 'SELECT name, description FROM vehicle_type WHERE id = %s;'
        cursor.execute(sql, (id,))
        vt_atual = cursor.fetchone()
        
        if not vt_atual:
            banco.close()
            return make_response(jsonify(mensagem='Tipo de veículo não encontrado para atualização.'), 404)

        dados_recebidos = request.get_json()
        
        # Mantém o valor atual se a chave correspondente não for enviada no JSON
        name = dados_recebidos.get('name', vt_atual[0])
        description = dados_recebidos.get('description', vt_atual[1])

        sql = 'UPDATE vehicle_type SET name=%s, description=%s WHERE id=%s;'
        cursor.execute(sql, (name, description, id))
        banco.commit()

        # Busca o registro modificado definitivo
        sql = 'SELECT id, name, description FROM vehicle_type WHERE id = %s;'
        cursor.execute(sql, (id,))
        vt = cursor.fetchone()
        banco.close()
        
        type_json = {
            "id": vt[0], #type:ignore
            "name": vt[1], #type:ignore
            "description": vt[2] #type:ignore
        }
        return make_response(jsonify(mensagem="Tipo de veículo atualizado com sucesso.", dados=type_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar tipo de veículo.", erro=str(e)), 500)


@app.route('/vehicle-types/<int:id>/', methods=['DELETE'])
@login_required
def delete_vehicle_type(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'SELECT id FROM vehicle_type WHERE id=%s;'
        cursor.execute(sql, (id,))
        vt = cursor.fetchone()
        
        if not vt:
            banco.close()
            return make_response(jsonify(mensagem='Tipo de veículo não encontrado para deletar.'), 404)

        sql = 'DELETE FROM vehicle_type WHERE id=%s;'
        cursor.execute(sql, (id,))
        banco.commit()
        banco.close()

        return make_response(jsonify(mensagem="Tipo de veículo deletado com sucesso."), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar tipo de veículo.", erro=str(e)), 500)
