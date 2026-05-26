from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from jwt_utils import token_requerido


@app.route('/vehicles/', methods=['GET'])
@token_requerido
def get_vehicles():
    try:
        banco = connect_db()
        cursor = banco.cursor()
        # Seleciona campos fundamentais para uma listagem otimizada
        sql = 'SELECT id, brand, model, license_plate FROM vehicle;'
        cursor.execute(sql)
        
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_vehicles_json = [
            {
                "id": vehicle[0],
                "brand": vehicle[1],
                "model": vehicle[2],
                "license_plate": vehicle[3],
            }
            for vehicle in resultado_fetchall
        ]

        lista_vehicles_json_ordenada = sorted(
            lista_vehicles_json,
            key=lambda x: x['id'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de Veículos.',
                total=len(lista_vehicles_json_ordenada),
                dados=lista_vehicles_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem='Erro interno ao listar veículos.', erro=str(e)), 500)


@app.route('/vehicles/<int:id>/', methods=['GET'])
@token_requerido
def get_vehicle(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()

        sql = 'SELECT id, brand, color, license_plate, model, owner_id, vehicle_type_id, created_at, updated_at FROM vehicle WHERE id = %s;'
        cursor.execute(sql, (id,))

        vehicle = cursor.fetchone()
        banco.close()

        if not vehicle:
            return make_response(
                jsonify(mensagem="Veículo não encontrado.", dados=vehicle), 404)
        
        vehicle_json = {
            "id": vehicle[0],
            "brand": vehicle[1],
            "color": vehicle[2],
            "license_plate": vehicle[3],
            "model": vehicle[4],
            "owner_id": vehicle[5],
            "vehicle_type_id": vehicle[6],
            "created_at": str(vehicle[7]),
            "updated_at": str(vehicle[8]),    
        }
        
        return make_response(jsonify(mensagem="Detalhe do Veículo.", dados=vehicle_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar veículo.", erro=str(e)), 500)


@app.route('/vehicles/', methods=['POST'])
@token_requerido
def create_vehicle():
    try:
        dados_recebidos = request.get_json()
        brand = dados_recebidos.get("brand")
        color = dados_recebidos.get("color")
        license_plate = dados_recebidos.get("license_plate")
        model = dados_recebidos.get("model")
        owner_id = dados_recebidos.get("owner_id")
        vehicle_type_id = dados_recebidos.get("vehicle_type_id")

        if not license_plate:
            return make_response(jsonify(mensagem="A placa do veículo (license_plate) é obrigatória."), 400)

        banco = connect_db()
        cursor = banco.cursor()

        # Validação Prévia: Verifica se o cliente (owner) realmente existe
        if owner_id:
            sql_check = 'SELECT id FROM customer WHERE id = %s;'
            cursor.execute(sql_check, (owner_id,))
            if not cursor.fetchone():
                banco.close()
                return make_response(jsonify(mensagem="O proprietário (owner_id) informado não existe."), 400)
            
        # Validação Prévia: Verifica se o vehicle type (vehicle_type_id) realmente existe
        if vehicle_type_id:
            sql_check = 'SELECT id FROM vehicle_type WHERE id = %s;'
            cursor.execute(sql_check, (vehicle_type_id,))
            if not cursor.fetchone():
                banco.close()
                return make_response(jsonify(mensagem="O Tipo de Veículo (vehicle_type_id) informado não existe."), 400)

        sql = 'INSERT INTO vehicle (brand, color, license_plate, model, owner_id, vehicle_type_id) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (brand, color, license_plate, model, owner_id, vehicle_type_id))
        banco.commit()

        id_criado = cursor.lastrowid
        sql = 'SELECT id, brand, color, license_plate, model, owner_id, vehicle_type_id, created_at, updated_at FROM vehicle WHERE id=%s;'
        cursor.execute(sql, (id_criado,))
        vehicle_criado = cursor.fetchone()
        banco.close()

        vehicle_json = {
            "id": vehicle_criado[0], #type:ignore
            "brand": vehicle_criado[1], #type:ignore
            "color": vehicle_criado[2], #type:ignore
            "license_plate": vehicle_criado[3], #type:ignore
            "model": vehicle_criado[4], #type:ignore
            "owner_id": vehicle_criado[5], #type:ignore
            "vehicle_type_id": vehicle_criado[6], #type:ignore
            "created_at": str(vehicle_criado[7]), #type:ignore
            "updated_at": str(vehicle_criado[8]), #type:ignore
        }

        return make_response(
            jsonify(
                mensagem="Veículo criado com sucesso.",
                dados=vehicle_json
            ),
            201
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar veículo.", erro=str(e)), 500)


@app.route('/vehicles/<int:id>/', methods=['PUT'])
@token_requerido
def put_vehicle(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()

        sql = 'SELECT id, brand, color, license_plate, model, owner_id, vehicle_type_id FROM vehicle WHERE id=%s;'
        cursor.execute(sql, (id,))
        vehicle = cursor.fetchone()
        if not vehicle:
            banco.close()
            return make_response(
                jsonify(
                    mensagem='Veículo não encontrado para atualização.'
                ), 
                404
            )

        dados_recebido = request.get_json()
        brand_recebido = dados_recebido.get('brand', vehicle[1])
        color_recebido = dados_recebido.get('color', vehicle[2])
        plate_recebido = dados_recebido.get('license_plate', vehicle[3])
        model_recebido = dados_recebido.get('model', vehicle[4])
        owner_recebido = dados_recebido.get('owner_id', vehicle[5])
        type_recebido = dados_recebido.get('vehicle_type_id', vehicle[6])

        sql = 'UPDATE vehicle SET brand=%s, color=%s, license_plate=%s, model=%s, owner_id=%s, vehicle_type_id=%s WHERE id=%s'
        cursor.execute(sql, (brand_recebido, color_recebido, plate_recebido, model_recebido, owner_recebido, type_recebido, id))
        banco.commit()

        sql = "SELECT id, brand, color, license_plate, model, owner_id, vehicle_type_id, created_at, updated_at FROM vehicle WHERE id=%s;"
        cursor.execute(sql, (id,))
        vehicle_atualizado = cursor.fetchone()
        banco.close()
        
        vehicle_json = {
            "id": vehicle_atualizado[0], #type:ignore
            "brand": vehicle_atualizado[1], #type:ignore
            "color": vehicle_atualizado[2], #type:ignore
            "license_plate": vehicle_atualizado[3], #type:ignore
            "model": vehicle_atualizado[4], #type:ignore
            "owner_id": vehicle_atualizado[5], #type:ignore
            "vehicle_type_id": vehicle_atualizado[6], #type:ignore
            "created_at": str(vehicle_atualizado[7]), #type:ignore
            "updated_at": str(vehicle_atualizado[8]),    #type:ignore
        }
        
        return make_response(
            jsonify(
                mensagem="Veículo atualizado com sucesso.",
                dados=vehicle_json
            ),
            200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar o veículo.", erro=str(e)), 500)


@app.route('/vehicles/<int:id>/', methods=['DELETE'])
@token_requerido
def delete_vehicle(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'SELECT id FROM vehicle WHERE id=%s;'
        cursor.execute(sql, (id,))
        vehicle = cursor.fetchone()
        if not vehicle:
            banco.close()
            return make_response(
                jsonify(
                    mensagem='Veículo não encontrado para deletar.',
                ),
                404
            )

        sql = 'DELETE FROM vehicle WHERE id=%s;'
        cursor.execute(sql, (id,))
        banco.commit()
        banco.close()

        return make_response(
            jsonify(
                mensagem="Veículo deletado com sucesso."
            ),
            200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar o veículo.", erro=str(e)), 500)
