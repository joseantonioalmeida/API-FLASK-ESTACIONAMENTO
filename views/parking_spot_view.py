from app import app
from db.connect_db import connect_db
from flask import make_response, jsonify, request
from datetime import datetime
from utils import login_required


def check_and_release_expired_spots(cursor):
    """
    Função utilitária para liberar automaticamente no banco de dados
    as vagas cujo tempo de ocupação já expirou, garantindo que não 
    afete novas reservas ativas na mesma vaga.
    """
    sql = """
        UPDATE parking_spot pr_spot
        SET pr_spot.is_occupied = 0
        WHERE pr_spot.is_occupied = 1
          AND pr_spot.id NOT IN (
              -- Mantém ocupada se houver algum registro onde o tempo de saída ainda não chegou
              SELECT DISTINCT parking_spot_id
              FROM parking_record
              WHERE exit_time > NOW() 
                AND parking_spot_id IS NOT NULL
          )
    """
    cursor.execute(sql)

@app.route('/parking-spots/', methods=['GET'])
@login_required
def get_parking_spots():
    try:
        banco = connect_db()
        cursor = banco.cursor()

        # Atualiza o status caso o tempo de algum registro tenha expirado
        check_and_release_expired_spots(cursor)
        banco.commit()

        # Seleciona todas as colunas da tabela parking_spot
        sql = 'SELECT id, spot_number, is_occupied, created_at, updated_at FROM parking_spot;'
        cursor.execute(sql)
        resultado_fetchall = cursor.fetchall()
        banco.close()

        lista_spots_json = [
            {
                "id": spot[0],
                "spot_number": spot[1],
                "is_occupied": bool(spot[2]),  # Converte tinyint(1) para True/False
                "created_at": str(spot[3]),
                "updated_at": str(spot[4])
            }
            for spot in resultado_fetchall
        ]

        lista_spots_json_ordenada = sorted(
            lista_spots_json,
            key=lambda x: x['spot_number'],
            reverse=True
        )

        return make_response(
            jsonify(
                mensagem='Lista de vagas de estacionamento.',
                total=len(lista_spots_json_ordenada),
                dados=lista_spots_json_ordenada
            ), 200
        )
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao listar vagas.", erro=str(e)), 500)


@app.route('/parking-spots/<int:id>/', methods=['GET'])
@login_required
def get_parking_spot_detail(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        # Atualiza o status caso o tempo de algum registro tenha expirado
        check_and_release_expired_spots(cursor)
        banco.commit()
        
        sql = 'SELECT id, spot_number, is_occupied, created_at, updated_at FROM parking_spot WHERE id = %s;'
        cursor.execute(sql, (id,))
        spot = cursor.fetchone()
        banco.close()

        if not spot:
            return make_response(jsonify(mensagem="Vaga não encontrada."), 404)
        
        spot_json = {
            "id": spot[0],
            "spot_number": spot[1],
            "is_occupied": bool(spot[2]),
            "created_at": str(spot[3]),
            "updated_at": str(spot[4])
        }
        return make_response(jsonify(mensagem="Detalhes da vaga.", dados=spot_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao buscar vaga.", erro=str(e)), 500)


@app.route('/parking-spots/', methods=['POST'])
@login_required
def create_parking_spot():
    try:
        dados_recebidos = request.get_json()
        
        spot_number = dados_recebidos.get("spot_number")
        is_occupied = dados_recebidos.get("is_occupied", 0) 

        if not spot_number:
            return make_response(jsonify(mensagem="O número da vaga (spot_number) é obrigatório."), 400)

        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'INSERT INTO parking_spot (spot_number, is_occupied) VALUES (%s, %s);'
        cursor.execute(sql, (spot_number, is_occupied))
        banco.commit()

        id_criado = cursor.lastrowid
        
        sql = 'SELECT id, spot_number, is_occupied, created_at, updated_at FROM parking_spot WHERE id = %s;'
        cursor.execute(sql, (id_criado,))
        s = cursor.fetchone()
        banco.close()

        spot_json = {
            "id": s[0], #type:ignore
            "spot_number": s[1], #type:ignore
            "is_occupied": bool(s[2]), #type:ignore
            "created_at": str(s[3]), #type:ignore
            "updated_at": str(s[4]) #type:ignore
        }
        return make_response(jsonify(mensagem="Vaga criada com sucesso.", dados=spot_json), 201)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao criar vaga.", erro=str(e)), 500)


@app.route('/parking-spots/<int:id>/', methods=['PUT'])
@login_required
def put_parking_spot(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        # Validação prévia para saber se o registro existe no banco
        sql = 'SELECT spot_number, is_occupied FROM parking_spot WHERE id = %s;'
        cursor.execute(sql, (id,))
        spot_atual = cursor.fetchone()
        
        if not spot_atual:
            banco.close()
            return make_response(jsonify(mensagem='Vaga não encontrada para atualização.'), 404)

        dados_recebidos = request.get_json()
        
        # Mantém o valor atual se o campo não for repassado no JSON da requisição
        spot_number = dados_recebidos.get('spot_number', spot_atual[0])
        is_occupied = dados_recebidos.get('is_occupied', spot_atual[1])

        sql = 'UPDATE parking_spot SET spot_number=%s, is_occupied=%s WHERE id=%s;'
        cursor.execute(sql, (spot_number, is_occupied, id))
        banco.commit()

        # Busca o registro atualizado
        sql = 'SELECT id, spot_number, is_occupied, created_at, updated_at FROM parking_spot WHERE id = %s;'
        cursor.execute(sql, (id,))
        s = cursor.fetchone()
        banco.close()
        
        spot_json = {
            "id": s[0], #type:ignore
            "spot_number": s[1], #type:ignore
            "is_occupied": bool(s[2]), #type:ignore
            "created_at": str(s[3]), #type:ignore
            "updated_at": str(s[4]) #type:ignore
        }
        return make_response(jsonify(mensagem="Vaga atualizada com sucesso.", dados=spot_json), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao atualizar vaga.", erro=str(e)), 500)


@app.route('/parking-spots/<int:id>/', methods=['DELETE'])
@login_required
def delete_parking_spot(id):
    try:
        banco = connect_db()
        cursor = banco.cursor()
        
        sql = 'SELECT id FROM parking_spot WHERE id=%s;'
        cursor.execute(sql, (id,))
        spot = cursor.fetchone()
        
        if not spot:
            banco.close()
            return make_response(jsonify(mensagem='Vaga não encontrada para deletar.'), 404)

        sql = 'DELETE FROM parking_spot WHERE id=%s;'
        cursor.execute(sql, (id,))
        banco.commit()
        banco.close()

        return make_response(jsonify(mensagem="Vaga deletada com sucesso."), 200)
    except Exception as e:
        return make_response(jsonify(mensagem="Erro interno ao deletar vaga.", erro=str(e)), 500)
