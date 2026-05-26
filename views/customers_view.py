from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from jwt_utils import token_requerido


@app.route('/customers/', methods=['GET'])
@token_requerido
def get_customers():
    try:
        banco = connect_db()
        cursor = banco.cursor()
        sql = 'SELECT id, name, phone FROM customer;'
        cursor.execute(sql)
        
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_customers_json = [
            {
                "id":customer[0],
                "nome":customer[1],
                "phone":customer[2],
            }
            for customer in resultado_fetchall
        ]

        lista_customers_json_ordenada = sorted(
            lista_customers_json,
            key=lambda x: x['id'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de Clientes.',
                total=len(lista_customers_json_ordenada),
                dados=lista_customers_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem='Erro interno ao listar clientes.', erro=str(e)), 500)

@app.route('/customers/<int:id>/', methods=['GET'])
@token_requerido
def get_customer(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()

        sql = 'select id, user_id, name, cpf, phone, created_at, updated_at FROM customer WHERE id = %s;'
        cursor.execute(sql, (id,))

        customer = cursor.fetchone()
        banco.close()

        if not customer:
            return make_response(
                jsonify(mensagem="Customer não encontrado.", dados=customer), 404)
        
        customer_json = {
                "id": customer[0],
                "user_id":customer[1],
                "name": customer[2],
                "cpf": customer[3],
                "phone":customer[4],
                "created_at": str(customer[5]),
                "updated_at": str(customer[6]),    
            }
        
        return make_response(jsonify(mensagem="Detalhe do Cliente.", dados=customer_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar cliente.", erro=str(e)), 500)


@app.route('/customers/', methods=['POST'])
@token_requerido
def create_customer():
    try:
        dados_recebidos = request.get_json()
        name_customer = dados_recebidos.get("name")
        cpf_customer = dados_recebidos.get("cpf")
        phone_customer = dados_recebidos.get("phone")

        if not name_customer or not cpf_customer:
            return make_response(jsonify(mensagem="Nome e CPF são obrigatórios."), 400)

        banco = connect_db()
        cursor = banco.cursor()

        sql = 'INSERT INTO customer (name, cpf, phone) values(%s, %s, %s)'
        cursor.execute(sql, (name_customer, cpf_customer, phone_customer))
        banco.commit()

        id_criado = cursor.lastrowid
        sql = 'SELECT id, user_id, name, cpf, phone, created_at, updated_at FROM customer WHERE id=%s;'
        cursor.execute(sql, (id_criado,))
        customer_criado = cursor.fetchone()
        banco.close()

        customer_json ={
                "id": customer_criado[0], #type:ignore
                "user_id":customer_criado[1], #type:ignore
                "name": customer_criado[2], #type:ignore
                "cpf": customer_criado[3], #type:ignore
                "phone":customer_criado[4], #type:ignore
                "created_at": str(customer_criado[5]), #type:ignore
                "updated_at": str(customer_criado[6]), #type:ignore
            }

        return make_response(
            jsonify(
                mensagem="Cliente criado com sucesso.",
                dados=customer_json
            ),
            201
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar cliente.", erro=str(e)), 500)

@app.route('/customers/<int:id>/', methods=['PUT'])
@token_requerido
def put_customer(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()

        sql = 'SELECT id, name, cpf, phone FROM customer WHERE id=%s;'
        cursor.execute(sql, (id,))
        customer = cursor.fetchone()
        if not customer:
            banco.close()
            return make_response(
                jsonify(
                    mensagem='Cliente não encontrado para atualização.'
                ), 
                404
            )

        dados_recebido = request.get_json()
        name_recebido = dados_recebido.get('name', customer[1])
        cpf_recebido = dados_recebido.get('cpf', customer[2])
        phone_recebido = dados_recebido.get('phone', customer[3])

        sql = 'update customer set name=%s, cpf=%s, phone=%s where id=%s'
        cursor.execute(sql,(name_recebido, cpf_recebido, phone_recebido, id,))
        banco.commit()

        sql = "select id, user_id, name, cpf, phone, created_at, updated_at from customer where id=%s;"
        cursor.execute(sql, (id,))
        customer_atualizado = cursor.fetchone()
        banco.close()
        
        customer_json = {
            "id": customer_atualizado[0], #type:ignore
            "user_id": customer_atualizado[1], #type:ignore
            "name": customer_atualizado[2], #type:ignore
            "cpf": customer_atualizado[3], #type:ignore
            "phone": customer_atualizado[4], #type:ignore
            "created_at": str(customer_atualizado[5]), #type:ignore
            "updated_at": str(customer_atualizado[6]),    #type:ignore
            }
        
        return make_response(
            jsonify(
                mensagem="Cliente atualizado com sucesso.",
                dados=customer_json
            ),
            200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar o cliente.", erro=str(e)), 500)

@app.route('/customers/<int:id>/', methods=['DELETE'])
@token_requerido
def delete_customer(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'select id from customer where id=%s;'
        cursor.execute(sql, (id,))
        customer = cursor.fetchone()
        if not customer:
            banco.close()
            return make_response(
                jsonify(
                    mensagem='Cliente não encontrado para deletar.',
                ),
                404
            )

        sql = 'delete from customer where id=%s;'
        cursor.execute(sql,(id,))
        banco.commit()
        banco.close()

        return make_response(
            jsonify(
                mensagem="Cliente deletado com sucesso."
            ),
            200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar o cliente.", erro=str(e)), 500)